"""
knowledge_base.py — Clinical Guideline Knowledge Base (RAG)
=============================================================
Implements Retrieval-Augmented Generation (RAG) for the clinical agents using
a lightweight in-memory vector store — no external database required.

How it works:
  1. On startup, clinical guidelines are loaded from clinical_rag_guidelines.csv
     (50 guidelines from CDC, WHO, AHA, FDA, KDIGO and other authorities).
  2. Each guideline's content is embedded into a vector using Ollama's
     nomic-embed-text model (running locally in the `ollama` container, no
     API key) and kept in memory alongside the guideline.
  3. When an agent calls search_clinical_guidelines(), the query is embedded
     the same way and compared against every stored guideline using cosine
     similarity — so "chest tightness and sweating" retrieves AHA chest pain
     guidelines even though neither phrase matches the other exactly.
  4. If embeddings can't be computed (e.g. Ollama is unreachable), a keyword
     fallback searches the guidelines directly so agents are never left
     without any guidelines at all.

Why in-memory instead of a vector database:
  50 guidelines is a small, fixed corpus — a full vector database (IRIS,
  Pinecone, Chroma, pgvector, ...) is unneeded infrastructure for this size.
  Cosine similarity over 50 float arrays is sub-millisecond in pure Python,
  and keeping it in-process means the knowledge base has zero external
  dependencies and works identically regardless of which FHIR server the
  agents are pointed at.
"""

import csv
import math
import httpx
from langchain.tools import tool
from config import OLLAMA_BASE_URL, EMBEDDING_MODEL, RAG_GUIDELINES_CSV

# ── In-memory store ───────────────────────────────────────────────────────────
# Each entry: {"id", "source", "topic", "content", "embedding"}
_GUIDELINES: list = []


# ═══════════════════════════════════════════════════════════════════════════════
#  DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def load_guidelines_from_csv() -> list:
    """
    Read the clinical guidelines CSV into memory.

    The CSV has four columns: id, source, topic, content.
    All values are stripped of leading/trailing whitespace to prevent
    embedding differences caused by invisible characters.
    """
    guidelines = []
    try:
        with open(RAG_GUIDELINES_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                guidelines.append({
                    "id":      row["id"].strip(),
                    "source":  row["source"].strip(),
                    "topic":   row["topic"].strip(),
                    "content": row["content"].strip()
                })
        print(f"RAG: Loaded {len(guidelines)} guidelines from CSV")
    except FileNotFoundError:
        print(f"RAG: WARNING — CSV not found at {RAG_GUIDELINES_CSV}. No guidelines loaded.")
    except Exception as e:
        print(f"RAG: ERROR reading CSV: {e}")
    return guidelines


# ═══════════════════════════════════════════════════════════════════════════════
#  EMBEDDINGS
# ═══════════════════════════════════════════════════════════════════════════════

def get_embedding(text: str) -> list:
    """
    Convert a text string into an embedding vector via the local Ollama
    server (nomic-embed-text by default) — no external API, no API key.
    """
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=30.0
    )
    response.raise_for_status()
    return [float(x) for x in response.json()["embedding"]]


def cosine_similarity(a: list, b: list) -> float:
    """Cosine similarity between two equal-length vectors."""
    dot   = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ═══════════════════════════════════════════════════════════════════════════════
#  KEYWORD FALLBACK
# ═══════════════════════════════════════════════════════════════════════════════

def keyword_search(query: str, guidelines: list) -> list:
    """
    Simple word-overlap search against the guidelines list.
    Runs when embeddings are unavailable (e.g. Ollama unreachable).
    """
    keywords = [w.lower() for w in query.split() if len(w) > 3]
    scored = []
    for g in guidelines:
        text = (g["topic"] + " " + g["content"]).lower()
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scored.append((score, {**g, "similarity": min(0.5 + score * 0.05, 0.95)}))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [r for _, r in scored[:3]]
    print(f"RAG: Keyword fallback found {len(results)} result(s)")
    return results


# ═══════════════════════════════════════════════════════════════════════════════
#  INITIALISATION — runs once when the module is first imported
# ═══════════════════════════════════════════════════════════════════════════════

def initialize_knowledge_base():
    """
    Load guidelines from CSV and embed each one into memory.

    Idempotent within a process (guards against re-running on hot reload),
    and resilient — if embedding fails for some rows (or all of them, e.g.
    Ollama is unreachable), those rows are still kept for keyword fallback.
    """
    global _GUIDELINES

    if _GUIDELINES:
        return

    guidelines = load_guidelines_from_csv()
    if not guidelines:
        print("RAG: No guidelines to load — check CSV path.")
        return

    embedded = 0
    for g in guidelines:
        entry = {**g, "embedding": None}
        try:
            entry["embedding"] = get_embedding(g["content"])
            embedded += 1
        except Exception as e:
            print(f"RAG: WARNING — could not embed {g['id']}: {e}")
        _GUIDELINES.append(entry)

    print(f"RAG: Initialisation complete — {embedded}/{len(guidelines)} guidelines embedded in memory")


# ═══════════════════════════════════════════════════════════════════════════════
#  LANGCHAIN TOOL — exposed to all clinical agents
# ═══════════════════════════════════════════════════════════════════════════════

@tool
def search_clinical_guidelines(query: str) -> str:
    """
    Search clinical guidelines from CDC, WHO, AHA, FDA and other medical authorities
    using semantic similarity search.
    ALWAYS use this tool before making any clinical recommendation, symptom assessment,
    or drug interaction check. Cite the source in your response.
    """
    try:
        print(f"RAG: Searching for '{query}'")

        rows = []

        # ── Primary: in-memory cosine similarity over embedded guidelines ──────
        embedded = [g for g in _GUIDELINES if g["embedding"]]
        if embedded:
            try:
                query_embedding = get_embedding(query)
                scored = [
                    {**g, "similarity": cosine_similarity(query_embedding, g["embedding"])}
                    for g in embedded
                ]
                scored.sort(key=lambda r: r["similarity"], reverse=True)
                rows = [r for r in scored[:3] if r["similarity"] > 0.1]
                print(f"RAG: Vector search returned {len(rows)} relevant result(s)")
            except Exception as e:
                print(f"RAG: Vector search failed ({e}) — falling back to keyword search")

        # ── Fallback: keyword search ──────────────────────────────────────────
        if not rows:
            rows = keyword_search(query, _GUIDELINES or load_guidelines_from_csv())

        if not rows:
            return "No relevant clinical guidelines found."

        # ── Format for agent ──────────────────────────────────────────────────
        output = []
        for row in rows:
            source    = row.get("source", "Unknown")
            topic     = row.get("topic", "")
            content   = row.get("content", "")
            relevance = round(float(row.get("similarity", 0.5)) * 100, 1)
            output.append(
                f"[{source}] (Relevance: {relevance}%)\n"
                f"Topic: {topic}\n"
                f"{content}"
            )

        print(f"RAG: Returning {len(output)} guideline(s) to agent")
        return "\n\n---\n\n".join(output)

    except Exception as e:
        print(f"RAG: Search error: {e}")
        return f"Error searching guidelines: {str(e)}"


# Run on import — initialises before the first HTTP request arrives
initialize_knowledge_base()
