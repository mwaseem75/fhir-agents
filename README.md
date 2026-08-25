# FHIR Agents

A multi-agent clinical AI platform that runs against **any FHIR R4 server**. Five LangChain-powered agents — Triage, Specialist, Pharmacy, FHIR Server exploration, and unlimited user-defined Custom Agents — work together on top of live FHIR data, grounded by a 50-guideline clinical knowledge base. No-code Agent Builder included: design and deploy a new clinical agent without writing code.

Runs entirely on free infrastructure: [Groq](https://console.groq.com/keys) for chat completions (free tier, no credit card) and a local [Ollama](https://ollama.com/) container for RAG embeddings (no API key at all). The whole stack — FHIR server, embeddings, and API — comes up with one `docker-compose up`.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![FHIR R4](https://img.shields.io/badge/FHIR-R4-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

## Table of Contents

- [What's Inside](#whats-inside)
- [Features at a Glance](#features-at-a-glance)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [A Guided Tour](#a-guided-tour) — the tutorial
- [Demo Patients & Use Cases](#demo-patients--use-cases)
- [Analytics Dashboard](#analytics-dashboard)
- [Live Vitals Monitor](#live-vitals-monitor)
- [FHIR Server Agent](#fhir-server-agent)
- [Agent Builder](#agent-builder)
- [RAG — Clinical Guidelines Knowledge Base](#rag--clinical-guidelines-knowledge-base)
- [Pointing at a Different FHIR Server](#pointing-at-a-different-fhir-server)
- [Managing the Stack](#managing-the-stack)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)
- [Contributing](#contributing)

---

## What's Inside

| Agent | Role | Key Capability |
|---|---|---|
| **Triage Agent** | Patient intake | Urgency classification · FHIR Observation writes · SNOMED CT codes |
| **Specialist Agent** | Condition analysis | Comorbidity review · Referral planning · ServiceRequest writes |
| **Pharmacy Agent** | Medication safety | Drug interaction checks · Allergy conflict detection · MedicationRequest writes |
| **FHIR Server Agent** | FHIR exploration | Natural language FHIR queries · Capability explorer |
| **Custom Agents** | User-defined specialty | No-code Agent Builder · Configurable tools · 5 clinical templates · Routes automatically via orchestrator |

Every agent is grounded by a **clinical guideline knowledge base** — 50 guidelines from CDC, AHA/ACC, FDA, WHO, KDIGO, AAAAI, and ADA, embedded and retrieved by in-memory semantic similarity. No guideline citation means no recommendation.

---

## Features at a Glance

- **Runs against any FHIR R4 server** — bundled HAPI FHIR for local dev, or point at IRIS for Health, Firely, a cloud FHIR service, or any other FHIR R4 endpoint via one environment variable
- **No paid API required** — chat runs on Groq's free tier, embeddings run locally on Ollama; the only signup is a free Groq key
- **Dynamic multi-agent orchestration** — a zero-temperature LLM router classifies every message and dispatches to the correct agent automatically — including user-created custom agents
- **No-code Agent Builder** — design, configure, and test custom clinical agents via a visual UI; five built-in templates (Oncology, Geriatrics, Pediatrics, Cardiology, Nutrition); deployed instantly into the orchestrator
- **Zero-dependency RAG knowledge base** — 50 clinical guidelines embedded once and held in memory; cosine similarity search with no external vector database to run or manage
- **Full FHIR R4 write path** — agents create Observations, ServiceRequests, and MedicationRequests on the FHIR server with proper SNOMED CT and RxNorm coding
- **Live vitals monitoring** — SSE stream writes every reading to FHIR as a coded Observation; critical vitals auto-trigger the Triage Agent with a 30-second AI alert cooldown
- **FHIR Capability Explorer** — visual breakdown of what your FHIR server supports: interaction matrix, resource cards, donut charts, search param rankings
- **Voice input** — Web Speech API integration in Triage Chat and FHIR Agent; auto-detects language and switches voice recognition accordingly; auto-sends on final transcript
- **Multi-language support** — agents automatically detect and respond in the patient's language (English, Spanish, French, Mandarin); drug safety warnings appear in both languages; English handoff summary always included for clinical staff
- **Patient Picker** — modal browser loading live from your FHIR server; real-time search; clinical hints per patient; one-click session start
- **Five-page frontend** — consistent sidebar navigation, three themes (Dark / Light / Clinical), live agent network panel, language badge
- **20 rich demo patients** — covering CAD, HFrEF, T1DM/DKA, T2DM, CKD, lupus, COPD, oncology, geriatrics/polypharmacy, sickle cell, and complex hepatic disease

---

## How It Works

```
User message
     │
     ▼
Orchestrator  (temp=0 LLM router — classifies intent, picks an agent)
     │
     ├──► Triage Agent
     ├──► Specialist Agent
     ├──► Pharmacy Agent
     └──► Custom Agent(s)  (built with Agent Builder)
              │
              ▼
     Shared tool layer
       • FHIR reads   — get_patient, get_patient_conditions, …
       • FHIR writes  — create_triage_observation, create_service_request, …
       • search_clinical_guidelines  (RAG)
              │
     ┌────────┴────────┐
     ▼                 ▼
Your FHIR R4 server    In-memory RAG store
(bundled HAPI FHIR,    (50 guidelines, embedded once
 or IRIS / Firely /     via Ollama at startup)
 a cloud FHIR service)
```

Every LLM call — the router and every agent — goes to **Groq's free API**, an OpenAI-compatible endpoint, so the same `langchain_openai.ChatOpenAI` client is used throughout, just pointed at a different base URL. Every guideline embedding call goes to **Ollama**, running locally in its own container. No OpenAI account, credit card, or paid API of any kind is required anywhere in the stack.

Each conversation keeps its own `ConversationBufferMemory`, keyed by `session_id`, so the orchestrator can hand a conversation from one agent to another mid-session (e.g. Triage identifies a medication concern and hands off to Pharmacy) without losing context.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **AI Agents** | LangChain · Groq (`openai/gpt-oss-120b`) · ConversationBufferMemory |
| **RAG / Knowledge Base** | In-memory cosine similarity · Ollama (`nomic-embed-text`) |
| **FHIR Server** | Any FHIR R4 server · bundled HAPI FHIR for local dev |
| **Clinical Standards** | FHIR R4 · SNOMED CT · LOINC · UCUM · HL7 |
| **Backend** | Python 3.11 · FastAPI · httpx · SSE |
| **Frontend** | Vanilla HTML/CSS/JS · Syne · JetBrains Mono · Lato |
| **Infrastructure** | Docker Compose · 4 services (HAPI FHIR, Ollama, one-shot seed loader, API) |
| **Guidelines** | CDC · AHA/ACC · FDA · WHO · KDIGO · AAAAI · ADA |

---

## Project Structure

```
fhir-agents/
├── docker-compose.yml
├── .env.example                  ← template — copy to .env and add your Groq key
├── .env                          ← your secrets (gitignored, never commit)
├── Dockerfile.api                ← application container
│
├── src/python/
│   ├── api/
│   │   └── main.py               ← FastAPI server, all HTTP routes
│   │
│   ├── agent/
│   │   ├── config.py             ← centralised configuration
│   │   ├── dynamic_agent.py      ← create custom agent
│   │   ├── orchestrator.py       ← LLM router + session management
│   │   ├── triage_agent.py       ← patient intake agent
│   │   ├── specialist_agent.py   ← condition analysis agent
│   │   ├── pharmacy_agent.py     ← medication safety agent
│   │   ├── fhir_agent.py         ← FHIR server exploration agent
│   │   ├── fhir_tools.py         ← shared FHIR R4 tools
│   │   └── knowledge_base.py     ← in-memory RAG knowledge base
│   │
│   └── static/
│       ├── index.html            ← Triage Chat
│       ├── dashboard.html        ← Analytics Dashboard
│       ├── vitals.html           ← Live Vitals Monitor
│       ├── fhir_agent.html       ← FHIR Server Agent
│       └── agent_builder.html    ← Build Custom Agent
│
└── data/
    ├── fhir/
    │   └── demo_patients.json    ← FHIR synthetic data (20 patients, 255 resources)
    │
    └── RAG/
        └── clinical_rag_guidelines.csv   ← 50 guidelines for RAG
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running (or Docker Engine + Compose v2 on Linux)
- A free [Groq API key](https://console.groq.com/keys) — sign in, click **API Keys → Create API Key**, no credit card required. The free tier gives every model on Groq's hardware, rate-limited to 30 requests/min and 6,000 tokens/min — plenty for exploring this app, but a chatty custom agent that makes many tool calls in a row can occasionally slow down against that token budget. Add a card later (still $0 minimum spend) if you want higher limits.
- Nothing else — the bundled HAPI FHIR server needs no license, and RAG embeddings run locally via a bundled Ollama container (also no key required)

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/mwaseem75/fhir-agents.git
cd fhir-agents
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and paste in your Groq key:

```env
GROQ_API_KEY=gsk-your-real-key-here
```

All other defaults work out of the box with the Docker setup.

### 3. Start the stack

```bash
docker-compose up -d --build
```

This brings up four services, in dependency order:

1. **`fhir-agents-hapi`** — [HAPI FHIR](https://hapifhir.io/) R4 server, port `8080`
2. **`fhir-agents-ollama`** — local embeddings server; pulls the `nomic-embed-text` model (~270 MB) on first run
3. **`fhir-agents-seed`** — one-shot job that waits for HAPI FHIR to accept requests, then loads the 20 demo patients and their clinical data; exits once done
4. **`fhir-agents-api`** — the FastAPI application, port `8000`; only starts once the seed job succeeds and Ollama is healthy

First startup takes a couple of minutes — mostly the Ollama model pull and HAPI FHIR's own Spring Boot startup. Watch it happen:

```bash
docker-compose logs -f
```

You're ready when the API logs show:

```
RAG: Loaded 50 guidelines from CSV
RAG: Initialisation complete — 50/50 guidelines embedded in memory
INFO:     Application startup complete.
```

### 4. Open the application

| Page | URL |
|---|---|
| Triage Chat | http://localhost:8000 |
| Analytics Dashboard | http://localhost:8000/dashboard |
| Live Vitals Monitor | http://localhost:8000/vitals |
| FHIR Server Agent | http://localhost:8000/fhir-agent |
| Agent Builder | http://localhost:8000/agent-builder |

---

## A Guided Tour

A hands-on walkthrough of every page, in the order most people find natural. Takes about 10 minutes. Do this once after your first `docker-compose up` to see the whole platform work together.

### Step 1 — Talk to Triage Chat

Open **http://localhost:8000**. Type:

```
My patient ID is demo-010
```

The Triage Agent fetches James Anderson's FHIR record — conditions, allergies, medications — and greets him by name. Now describe a symptom:

```
I'm having chest tightness and sweating
```

Watch what happens: the agent classifies urgency, searches the RAG knowledge base for a matching guideline (you'll see it cited by name with a relevance score — e.g. *AHA/ACC Guidelines 2021, 74% relevance*), cross-checks the response against James's known **aspirin allergy** before suggesting anything, and writes a FHIR `Observation` and `ServiceRequest` back to the server. Everything it just wrote is now live FHIR data.

### Step 2 — See the write-back on the Dashboard

Open **http://localhost:8000/dashboard**. The **AI Observations** tab shows the Observation you just triggered, with the SNOMED-coded symptom, severity, and a timestamp — this page is a live audit trail of everything the agents write, not a static report.

### Step 3 — Watch Live Vitals

Open **http://localhost:8000/vitals** and pick a patient. Five vital-sign cards update every 2 seconds from a simulated bedside monitor, each write landing in FHIR as a coded Observation. Leave it running for a minute or two — the simulator occasionally spikes a reading past a critical threshold (e.g. SpO₂ below 90%), which auto-dispatches the Triage Agent with **no user action required**. When it fires, the **AI Critical Alert Feed** panel updates with the AI's assessment.

### Step 4 — Ask the FHIR Server Agent a question

Open **http://localhost:8000/fhir-agent**. Try:

```
How many patients are on this server, and what's the most common condition?
```

This agent has its own toolset (10 tools) purpose-built for exploring FHIR data rather than treating a single patient — population statistics, condition search, and the same guideline RAG search. Switch to the **Capability Explorer** tab to see a live visual breakdown of your FHIR server's `CapabilityStatement` — every resource type it supports, every interaction, straight from `GET /fhir/metadata`.

### Step 5 — Build your own agent

Open **http://localhost:8000/agent-builder**. Pick the **🎗️ Oncology** template (or start from a blank agent), review the pre-filled system prompt, and click **Test** — it runs against live FHIR data before you save anything. Once you're happy with it, click **Save**. It's now live: go back to Triage Chat and ask an oncology-flavored question (try loading `demo-022`, a breast cancer patient) — the orchestrator will route to your new agent automatically, no restart needed.

---

## Demo Patients & Use Cases

20 synthetic patients (`demo-010`–`demo-029`) ship pre-loaded, spanning a wide range of clinical complexity. A representative sample:

| Patient ID | Name | Conditions | Try With |
|---|---|---|---|
| `demo-010` | James Anderson, M/68 | CAD · Hypertension · Atrial Fibrillation | **Pharmacy** — Warfarin on board + high-criticality **aspirin allergy**; needs an antiplatelet alternative |
| `demo-011` | Maria Gonzalez, F/38 | T1DM · Septicaemia · Diabetic Ketoacidosis | **Triage/Emergency** — critical presentation; DKA management guideline retrieval |
| `demo-012` | Robert Davis, M/61 | T2DM · Hypertension · Diabetic Retinopathy · CKD Stage 3 | **Specialist** — multi-system comorbidity, nephrology + ophthalmology referral reasoning |
| `demo-013` | Patricia Taylor, F/76 | HFrEF · T2DM · CKD Stage 3 · Hypertension | **Specialist/Emergency** — decompensated heart failure, GDMT gap analysis |
| `demo-020` | Aisha Thompson, F/40 | Lupus · Lupus Nephritis · Anxiety | **Specialist** — autoimmune complexity, chronic disease management |
| `demo-021` | Thomas Brown, M/72 | COPD (severe) · Cor Pulmonale · Osteoporosis | **Specialist/Pharmacy** — respiratory + cardiac interaction |
| `demo-022` | Susan Lee, F/56 | Breast Cancer · T2DM · Hypertension | **Oncology custom agent** — build one via Agent Builder and test against this patient |
| `demo-026` | Dorothy Adams, F/88 | Alzheimer's (moderate) · Hypertension · Osteoporosis · Depression | **Geriatrics custom agent** — polypharmacy review, Beers Criteria screening |

Click **Browse patients** in any chat interface to open the live Patient Picker, or just type `My patient ID is demo-010` to start.

---

## Analytics Dashboard

The Analytics Dashboard (`/dashboard`) provides a real-time population-level view of all clinical data on the FHIR server, alongside a live record of every FHIR resource written by the AI agents during triage sessions.

**Overview** — four summary stat cards (Patients, Conditions, Medications, Allergies) queried live from the FHIR server, plus a Top Active Conditions bar chart, a Gender Distribution donut chart, and Recent Triage Observations.

**Patients** — a paginated roster of every patient on the server. Click any patient to expand Demographics, Active Conditions, Known Allergies, and Current Medications, all fetched live from FHIR.

**Conditions** — a full ranked bar chart of active conditions across the population, drilling down to affected patients.

**AI Observations** — every FHIR Observation the Triage Agent has written, with symptom, severity, patient reference, and timestamp — the live audit trail of AI clinical activity.

**Service Requests** — every FHIR ServiceRequest written by the Triage and Specialist agents, with referral type, priority, and clinical reason.

---

## Live Vitals Monitor

The Live Vitals Monitor (`/vitals`) is a real-time bedside monitoring simulation that streams patient vitals via Server-Sent Events (SSE), writes every reading to the FHIR server as a FHIR Observation, and automatically triggers the Triage Agent when critical values are detected — without any user action required.

Five vital sign cards (Heart Rate, Blood Pressure, SpO₂, Temperature, Respiratory Rate) update every 2 seconds with colour-coded status and a mini sparkline of the last 20 readings. The patient sidebar loads live from the FHIR server via `GET /analytics/patients` — no hardcoding.

When a vital crosses a critical threshold, the platform dispatches an assessment to the Triage Agent automatically, with a 30-second cooldown to prevent alert spam:

```
SSE reading arrives → FHIR Observation written
↓
Critical threshold crossed → Triage Agent dispatched
↓
RAG searches the clinical knowledge base for relevant guidelines
↓
AI assessment returned → AI Critical Alert Feed panel updated
↓
FHIR ServiceRequest written if referral is warranted
```

The Vitals History table shows the last 15 readings with a FHIR ✓ confirming every write.

---

## FHIR Server Agent

The FHIR Server Agent (`/fhir-agent`) provides two complementary ways to explore your FHIR R4 server — a **live visual Capability Explorer** and a **natural language AI chat** interface that can query patients, cross-reference clinical guidelines, and report server statistics.

**AI Chat** (default tab) — a conversational interface powered by Groq with 10 FHIR tools. Ask anything about your FHIR data in plain English.

**FHIR Capability Explorer** — a live visual breakdown of everything your FHIR server supports, loaded directly from the CapabilityStatement (`GET /fhir/metadata`) at page load: server info cards, summary stats, an Interaction Coverage donut chart, Resource Categories donut chart, Top Search Parameters bar chart, an Interaction Matrix for the eight key clinical resources, and a filterable grid of every supported resource.

### AI Chat — 10 FHIR tools

| Tool | What it does |
|---|---|
| `get_patient_list` | Fetch/browse patients from the FHIR server |
| `get_conditions_for_patient` | Get active conditions for a patient |
| `get_medications_for_patient` | Get active medications for a patient |
| `get_observations_for_patient` | Get observations and lab results |
| `get_allergies_for_patient` | Get allergy/intolerance records |
| `get_procedures_for_patient` | Get procedure history |
| `search_patients_by_condition` | Find patients across the population who have a given condition |
| `get_fhir_statistics` | Resource counts across the server |
| `get_full_patient_summary` | One-call full clinical snapshot for a patient |
| `search_clinical_guidelines` | RAG search of the clinical knowledge base |

The sidebar **Tools Used** panel tracks which tools have been called in the current session, with a call counter and a pulsing indicator when a tool is actively running.

---

## Agent Builder

The Agent Builder (`/agent-builder`) is a no-code interface for designing, configuring, and deploying custom AI clinical agents. Every agent created here integrates directly into the Triage Chat orchestrator, appears in the Agent Network sidebar, and is callable from the same conversation interface as the built-in agents.

### Five clinical templates

| Template | Specialty | Key Capabilities |
|---|---|---|
| 🎗️ **Oncology Agent** | Oncology | Chemotherapy drug interactions, platinum compound contraindications, tumour board referrals, NCCN/ASCO guideline citations |
| 👴 **Geriatrics Agent** | Geriatrics | Beers Criteria screening, anticholinergic burden, fall risk, polypharmacy review (≥5 drugs flagged) |
| 👶 **Pediatrics Agent** | Pediatrics | Weight-based dosing (mg/kg), age-appropriate normal ranges, contraindicated medications (aspirin, codeine, fluoroquinolones) |
| ❤️ **Cardiology Agent** | Cardiology | HFrEF/HFpEF management, digoxin + electrolyte danger detection, GDMT gap identification, AHA/ACC guidelines |
| 🥗 **Nutrition Agent** | Nutrition | Drug-nutrient interactions, disease-specific dietary guidance (ADA, KDOQI), warfarin + vitamin K counselling |

### How it works

Open Agent Builder → Choose a template or start blank → Write system prompt, configure tools, set temperature, enable RAG → Test against live FHIR data → Save → Available instantly in Triage Chat.

### What makes a good custom agent

| Setting | Guidance |
|---|---|
| **Temperature** | `0.1` for drug safety and strict protocols · `0.2` for clinical assessments · `0.3` for counselling and dietary advice |
| **System prompt** | Start with the specialty, list responsibilities, add clinical rules. The platform auto-appends patient ID injection, language detection, and guideline citation rules. |
| **Routing description** | One sentence telling the orchestrator when to route to this agent. Be specific: *"For cancer, chemotherapy, and oncology questions"* works better than *"For complex patients"*. |
| **Tools** | Enable `create_service_request` if the agent should write referrals. Enable `create_triage_observation` if it should record clinical findings. Disable write tools for read-only advisory agents. |
| **RAG** | Keep enabled for any clinical agent — guideline grounding prevents hallucinated recommendations. Note the system prompt always instructs the agent to call `search_clinical_guidelines` before recommending anything, so a topic with no matching guideline in the 50-row corpus (nutrition/lifestyle questions, for instance) can make the agent retry several searches before answering — expect a few extra seconds of latency in that case, not a hang. |

---

## RAG — Clinical Guidelines Knowledge Base

Every agent recommendation is grounded by **50 clinical guidelines**, embedded once at startup with Ollama's `nomic-embed-text` (running locally, no API key) and held in memory — no vector database to provision or manage. A query is embedded the same way and compared against every guideline with cosine similarity in pure Python; sub-millisecond at this corpus size. If embeddings are ever unavailable, a keyword-overlap fallback keeps the agents grounded.

The corpus covers CAD, heart failure, AFib, T1DM/T2DM, CKD, insulin therapy, metformin safety, and more — all sourced from CDC, AHA/ACC, FDA, WHO, KDIGO, AAAAI, and ADA. Add your own by appending rows to `data/RAG/clinical_rag_guidelines.csv` (columns: `id, source, topic, content`) and restarting the `api` container — new rows are embedded automatically on the next startup.

Try it: load a patient (`My patient ID is demo-012`) and ask a clinical question — the response cites the source guideline and relevance score.

---

## Pointing at a Different FHIR Server

Set `FHIR_BASE_URL` (and, if the server requires basic auth, `FHIR_USERNAME` / `FHIR_PASSWORD`) in `.env` or `docker-compose.yml`:

```env
FHIR_BASE_URL=https://your-fhir-server.example.com/fhir
FHIR_USERNAME=optional
FHIR_PASSWORD=optional
```

No code changes needed — every agent and tool reads the FHIR endpoint from `config.py`. This works with InterSystems IRIS for Health, Firely Server, a cloud FHIR service (Google/Azure/AWS), a public test server, or any other FHIR R4-compliant endpoint. Note that the bundled 20-patient demo dataset and the `seed` service are HAPI-specific conveniences — pointing at a different server just means you bring your own patient data (or skip the `seed` service in `docker-compose.yml`).

---

## Managing the Stack

**Stop everything** (containers stop, data persists in Docker volumes):
```bash
docker-compose down
```

**Start again** (no rebuild needed unless you changed dependencies):
```bash
docker-compose up -d
```

**Reset all data** — wipes the HAPI FHIR database and the downloaded Ollama model, next `up` re-seeds and re-pulls from scratch:
```bash
docker-compose down -v
```

**Rebuild after changing `requirements.txt` or `Dockerfile.api`**:
```bash
docker-compose up -d --build
```

**Tail logs for one service**:
```bash
docker logs -f fhir-agents-api      # application + agent activity
docker logs -f fhir-agents-hapi     # FHIR server
docker logs -f fhir-agents-ollama   # embeddings server
```

Code in `src/python/` is bind-mounted into the `api` container with `uvicorn --reload`, so editing an agent or the FastAPI app picks up the change immediately — no rebuild needed for Python-only edits.

---

## Troubleshooting

**`docker-compose up` fails immediately / "Cannot connect to the Docker daemon"** — Docker Desktop isn't running. Start it and wait for the whale icon in your menu bar/tray to stop animating, then retry.

**API container starts but nothing works, logs show a 401 from Groq** — `GROQ_API_KEY` in `.env` is missing, wrong, or still the placeholder. Get a real key from [console.groq.com/keys](https://console.groq.com/keys), update `.env`, then `docker-compose up -d` (no rebuild needed — it's just an env var).

**`fhir-agents-seed` exits with an error** — HAPI FHIR probably wasn't ready in time (the seed job retries for up to 2 minutes before giving up) or the container was mid-restart. Check `docker logs fhir-agents-hapi` for startup errors, then `docker-compose up -d` again — the seed data is idempotent, so re-running it is always safe.

**Custom agent responses are slow** — the platform's built-in RAG rule means every clinical agent tries `search_clinical_guidelines` before answering, and Groq's free tier caps at 6,000 tokens/minute. An agent that needs several tool-call rounds (or asks about a topic with no matching guideline, so it keeps retrying the search) can take 30–90 seconds on the free tier. This is a rate-limit tradeoff of the free tier, not a hang — it will complete.

**Port `8000` or `8080` already in use** — something else on your machine is bound to it. Either stop that process, or change the host-side port mapping in `docker-compose.yml` (e.g. `"8001:8000"`) and browse to the new port.

**Want a completely clean slate** — `docker-compose down -v` removes all containers, networks, and volumes (FHIR data + downloaded Ollama model), so the next `up` starts from zero.

---

## API Reference

### Pages

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Triage Chat |
| `GET` | `/dashboard` | Analytics Dashboard |
| `GET` | `/vitals` | Live Vitals Monitor |
| `GET` | `/fhir-agent` | FHIR Server Agent |
| `GET` | `/agent-builder` | Agent Builder |
| `GET` | `/health` | Service health check |

### Clinical Chat

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Multi-agent clinical chat — routed to built-in or custom agents |
| `GET` | `/session/{id}/new` | Clear session context and memory |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics/summary` | FHIR resource counts |
| `GET` | `/analytics/conditions` | Top active conditions across all patients |
| `GET` | `/analytics/observations` | AI-created triage observations |
| `GET` | `/analytics/service-requests` | AI-created service requests |
| `GET` | `/analytics/patients` | Patient roster — used by Patient Picker modal |

### Live Vitals

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/vitals/stream/{patient_id}` | SSE real-time vitals stream |
| `GET` | `/vitals/alerts` | AI-triggered critical alert feed |
| `GET` | `/vitals/snapshot/{patient_id}` | Single vitals reading |

### FHIR Server Agent

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/fhir-agent/chat` | FHIR Server Agent natural language chat |
| `GET` | `/fhir-agent/status` | FHIR server connectivity check |
| `GET` | `/fhir/metadata` | FHIR CapabilityStatement proxy |

### Custom Agent Builder

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/agents` | List all custom agents |
| `POST` | `/agents/create` | Create or update a custom agent |
| `DELETE` | `/agents/{agent_id}` | Delete a custom agent |
| `POST` | `/agents/{agent_id}/test` | Test a custom agent with a single message against the live FHIR server |

---

## Contributing

Issues and pull requests are welcome — this is a demo/reference platform, so contributions that add clinical guidelines, demo patients, custom agent templates, or support for another free-tier LLM/embedding provider are especially useful. If you're proposing a larger change (a new agent type, a different orchestration strategy), open an issue first to discuss the approach.

Licensed under the [MIT License](LICENSE).

Thanks
