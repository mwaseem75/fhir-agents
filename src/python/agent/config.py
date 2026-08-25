"""
config.py — Centralised Application Configuration
==================================================
Single source of truth for all environment-specific settings.

Every value here is read from an environment variable with a sensible
default for local Docker development. To deploy to a different environment
(staging, production, cloud), only the environment variables need to change —
no source files need to be edited.

Environment variables are set in docker-compose.yml under the api service.
For production, use Docker secrets or a secrets manager instead of
plain-text environment variables.

Usage in any module:
    from config import FHIR_BASE, FHIR_AUTH, FHIR_HEADERS, LLM_MODEL
"""

import os

# ── FHIR R4 server ─────────────────────────────────────────────────────────────
# Works with any FHIR R4-compliant server — HAPI FHIR, InterSystems IRIS for
# Health, Firely, Google/Azure/AWS FHIR services, or a vendor sandbox.
# Default points at the bundled HAPI FHIR container from docker-compose.yml.
FHIR_BASE = os.getenv("FHIR_BASE_URL", "http://hapi-fhir:8080/fhir")

# Basic auth credentials — optional. Most public/test FHIR servers (including
# the bundled HAPI FHIR container) need no auth at all, so both default to
# empty and FHIR_AUTH becomes None unless a username is explicitly set.
FHIR_USERNAME = os.getenv("FHIR_USERNAME", "")
FHIR_PASSWORD = os.getenv("FHIR_PASSWORD", "")
FHIR_AUTH     = (FHIR_USERNAME, FHIR_PASSWORD) if FHIR_USERNAME else None

# Standard headers for all FHIR REST requests.
# Content-Type is only needed on POST/PUT — included here for convenience
# so callers can pass FHIR_HEADERS to both GET and POST without thinking about it.
FHIR_HEADERS = {
    "Accept":       "application/fhir+json",
    "Content-Type": "application/fhir+json"
}

# ── Groq (chat LLM) ─────────────────────────────────────────────────────────────
# Groq's free tier (no credit card) serves an OpenAI-compatible API, so the
# existing langchain_openai.ChatOpenAI client works unchanged — just point it
# at Groq's base URL with a Groq key instead of OpenAI's.
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

# Model used by all clinical agents and the orchestrator router.
# openai/gpt-oss-120b is Groq's recommended replacement for the deprecated
# llama-3.3-70b-versatile on the free/developer tier.
LLM_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Per-agent temperatures — kept here so the reasoning behind each value
# is documented in one place rather than scattered across agent files:
#   TRIAGE     0.3 — patient-facing conversation needs natural, empathetic tone
#   SPECIALIST 0.2 — clinical reasoning benefits from some expressive prose
#   PHARMACY   0.1 — drug safety decisions are binary; minimise creativity
#   ROUTER     0.0 — deterministic single-word classification; no randomness
TEMP_TRIAGE     = float(os.getenv("TEMP_TRIAGE",     "0.3"))
TEMP_SPECIALIST = float(os.getenv("TEMP_SPECIALIST", "0.2"))
TEMP_PHARMACY   = float(os.getenv("TEMP_PHARMACY",   "0.1"))
TEMP_ROUTER     = float(os.getenv("TEMP_ROUTER",     "0.0"))

# ── RAG Knowledge Base ────────────────────────────────────────────────────────
# Path to the clinical guidelines CSV inside the container.
# Mounted from host data/guidelines/ via docker-compose volume so guidelines
# can be updated without rebuilding the image.
RAG_GUIDELINES_CSV = os.getenv(
    "RAG_GUIDELINES_CSV",
    "/app/data/RAG/clinical_rag_guidelines.csv"
)

# Ollama (embeddings only) — runs locally as the `ollama` docker-compose
# service, no API key needed. Groq doesn't serve embedding models, so
# embeddings stay local while chat completions go to Groq's cloud API.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

# Embedding model used for the in-memory guideline search — see
# knowledge_base.py. Changing this only affects freshly computed embeddings;
# no schema/migration concerns since there's no external vector store.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# ── Application ───────────────────────────────────────────────────────────────
APP_TITLE   = "FHIR Agents"
APP_VERSION = "2.0.0"
APP_DESC    = (
    "Multi-agent AI clinical platform that runs against any FHIR R4 server. "
    "Triage, Specialist, Pharmacy, and FHIR Server agents powered by Groq, "
    "grounded by a clinical guideline knowledge base."
)
