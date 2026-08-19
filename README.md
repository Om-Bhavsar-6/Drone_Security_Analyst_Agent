# 🛸 Autonomous Drone Security Analyst Agent

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite FTS5](https://img.shields.io/badge/Search-SQLite_FTS5-003B57.svg)](https://sqlite.org/fts5.html)
[![Tests](https://img.shields.io/badge/Tests-19%20Passed%20(100%25)-brightgreen.svg)]()
[![FlytBase Assignment](https://img.shields.io/badge/FlytBase-AI%20Engineer%20Assignment-orange.svg)]()

A production-grade, multimodal AI surveillance platform designed for docked drones patrolling industrial properties. The system ingests synchronized video frames and telemetry, performs dense structured Vision-Language Model (VLM) extraction, persists indexed frames in SQLite FTS5 for sub-millisecond lexical search, tracks temporal entity states across frames, calculates multi-factor threat severity scores, and exposes an intelligent tool-using Conversational Security Analyst Agent.

---

## 🏗️ System Architecture

```
                         ┌─────────────────────────┐
                         │ Drone / Simulator       │
                         │                         │
                         │ Telemetry + Video       │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Ingestion Layer         │
                         │                         │
                         │ • frame_id              │
                         │ • timestamp             │
                         │ • telemetry sync        │
                         │ • validation            │
                         └────────────┬────────────┘
                                      │
                                      ▼
                    ┌──────────────────────────────────┐
                    │ Multimodal Analysis Pipeline     │
                    │                                  │
                    │  VLM / Mock VLM                  │
                    │        │                         │
                    │        ▼                         │
                    │  Structured Observation          │
                    │  • objects                       │
                    │  • people                        │
                    │  • vehicles                      │
                    │  • activities                    │
                    │  • confidence                    │
                    │  • description                   │
                    └────────────────┬─────────────────┘
                                     │
                  ┌──────────────────┼──────────────────┐
                  │                  │                  │
                  ▼                  ▼                  ▼
          ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
          │ Event Store  │   │ Search Index │   │ Alert Engine │
          │ SQLite       │   │ FTS5         │   │ Rule Engine  │
          │              │   │              │   │              │
          │ frames       │   │ descriptions │   │ time rules   │
          │ telemetry    │   │ objects      │   │ loitering    │
          │ observations │   │ locations    │   │ recurrence   │
          │ alerts       │   │ events       │   │ severity     │
          └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    ▼
                         ┌─────────────────────────┐
                         │ Agent / Query Layer     │
                         │                         │
                         │ /logs                   │
                         │ /alerts                 │
                         │ /search                 │
                         │ /chat                   │
                         │ /summary                │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Operator / Dashboard    │
                         │                         │
                         │ Timeline                │
                         │ Alerts                  │
                         │ Search                  │
                         │ Conversational QA       │
                         └─────────────────────────┘
```

---

## 🌟 Key Engineering Highlights

1. **Decoupled Modular Architecture**: Clean separation between API, Ingestion, Storage, AI/VLM, Detection, and Agent layers.
2. **Durable Relational Persistence (SQLite + FTS5)**: Eliminates volatile in-memory storage; uses SQLite as the single source of truth and FTS5 with BM25 ranking for instant lexical search.
3. **Structured VLM Outputs**: VLM generates strongly-typed `StructuredObservation` models (`objects`, `activities`, `risk_indicators`) rather than arbitrary text strings.
4. **Stateful Cross-Frame Entity Tracking**: Correlates entities over time (e.g., detecting a Blue Ford F150 entering at 12:00 at the Garage and exiting at 14:30 at the Main Gate).
5. **Decoupled Risk vs Confidence Engine**: Differentiates model detection confidence (0.95) from threat severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) using multi-factor weighted scoring.
6. **Tool-Using Conversational Analyst Agent (`/chat`)**: Dynamically executes forensic tools (`search_frames`, `get_events`, `get_alerts`) to synthesize context-aware security answers with referenced frame IDs.
7. **Automated Mission Summarization (`/summary`)**: Bonus feature generating high-level operational shift briefings.
8. **100% Verified QA Test Suite**: 19 automated unit, integration, API, and failure-handling tests (clock drift, duplicate frame rejection, boundary validation).

---

## 📁 Project Directory Structure

```text
drone_security_agent/
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application & lifespan management
│   │
│   ├── api/                        # REST API routers
│   │   ├── __init__.py
│   │   ├── health.py               # Health & status endpoint
│   │   ├── logs.py                 # Structural logs & frame details
│   │   ├── alerts.py               # Security alerts retrieval
│   │   ├── events.py               # Tracked entity recurrence profiles
│   │   ├── search.py               # Hybrid FTS5 & metadata search
│   │   ├── chat.py                 # Conversational Security Analyst
│   │   ├── summary.py              # Bonus mission summary endpoint
│   │   └── pipeline.py             # Background stream controls
│   │
│   ├── core/                       # Core configuration & logging
│   │   ├── config.py               # Pydantic Settings & environment variables
│   │   ├── logging.py              # Structured telemetry/inference logger
│   │   └── lifecycle.py
│   │
│   ├── models/                     # Strongly-typed domain models
│   │   ├── telemetry.py            # Drone telemetry schema
│   │   ├── frame.py                # Video frame packet
│   │   ├── observation.py          # Structured VLM schema
│   │   ├── alert.py                # Alert schema & severity levels
│   │   ├── event.py                # Cross-frame entity entity
│   │   └── query.py                # Search & Chat request/response schemas
│   │
│   ├── pipeline/                   # Stream ingestion & orchestration
│   │   ├── simulator.py            # Coherent narrative flight dataset
│   │   ├── synchronizer.py         # Timestamp & telemetry validator
│   │   ├── processor.py            # End-to-end frame processing logic
│   │   └── orchestrator.py         # Asyncio background pipeline manager
│   │
│   ├── ai/                         # Multimodal VLM engine
│   │   ├── base.py                 # Base VLM interface
│   │   ├── mock_vlm.py             # Deterministic high-fidelity mock VLM
│   │   ├── gemini_vlm.py           # Real Gemini / API VLM adapter
│   │   ├── vlm_engine.py           # VLM factory
│   │   └── prompts.py              # Structured security vision prompts
│   │
│   ├── detection/                  # Alerting & Risk rules
│   │   ├── severity.py             # Multi-factor risk calculation engine
│   │   ├── rules.py                # Night loitering & vehicle recurrence rules
│   │   └── event_tracker.py        # Stateful cross-frame entity tracker
│   │
│   ├── storage/                    # Persistence layer
│   │   ├── database.py             # SQLite connection & FTS5 schema initializer
│   │   └── repositories.py         # Frame, Observation, Alert, Event repositories
│   │
│   ├── search/                     # Hybrid & FTS5 search
│   │   ├── fts.py                  # SQLite FTS5 indexer and BM25 ranker
│   │   └── retriever.py            # Structured + FTS hybrid retriever
│   │
│   └── agent/                      # Security Analyst Agent
│       ├── context.py              # Timeline & context builder
│       ├── tools.py                # Search, alert, event, and timeline tools
│       └── assistant.py            # Tool-invoking conversational analyst
│
├── data/                           # SQLite database storage
├── notebooks/
│   └── sandbox.ipynb               # Interactive Jupyter sandbox
│
├── docs/                           # Architectural Artifacts
│   ├── architecture.md             # System architecture & component deep-dive
│   ├── demo_script.md              # 3-5 min voiceover video recording playbook
│   └── ai_tool_log.md              # AI-Assisted co-working report
│
├── tests/                          # Production QA Test Suite (19 tests)
│   ├── conftest.py                 # Test fixtures & temporary in-memory DB
│   ├── test_simulator.py           # Telemetry & frame simulation tests
│   ├── test_synchronizer.py        # Timestamp sync & idempotency tests
│   ├── test_vlm.py                 # Structured VLM output tests
│   ├── test_rules.py               # Loitering, recurrence, & severity tests
│   ├── test_event_tracker.py       # Cross-frame entity state tracking tests
│   ├── test_storage.py             # SQLite persistence & FTS5 search tests
│   ├── test_agent.py               # Tool selection & Chat QA tests
│   ├── test_api.py                 # FastAPI endpoints integration tests
│   └── test_failure_handling.py    # Malformed telemetry, duplicate frames
│
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── design_report.md                # In-depth 22-section Architectural Justification
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Setup Virtual Environment & Dependencies
```bash
# Clone the repository
git clone <repo_url>
cd drone_security_agent

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Drone Security SOC Dashboard & API
```bash
python dashboard.py
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Once started:
- **Interactive Security Operations Dashboard (NiceGUI)**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger REST API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Automated QA Tests

Execute the full suite of 19 automated tests:
```bash
python -m pytest
```

Output:
```text
============================= test session starts =============================
collected 19 items

tests/test_agent.py ..                                                   [ 10%]
tests/test_api.py ......                                                 [ 42%]
tests/test_event_tracker.py .                                            [ 47%]
tests/test_failure_handling.py ..                                        [ 57%]
tests/test_rules.py ..                                                   [ 68%]
tests/test_simulator.py .                                                [ 73%]
tests/test_storage.py .                                                  [ 78%]
tests/test_synchronizer.py ..                                            [ 89%]
tests/test_vlm.py ..                                                     [100%]

============================= 19 passed in 2.89s ==============================
```

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health diagnostics, index statistics, and pipeline state |
| `GET` | `/logs` | Fetch all ingested frames, telemetry, and VLM observations |
| `GET` | `/logs/{frame_id}` | Fetch detailed timeline data for a single frame |
| `GET` | `/alerts` | Retrieve security alerts (with optional `min_severity` filter) |
| `GET` | `/alerts/{alert_id}`| Get full metadata for a specific security alert |
| `GET` | `/events` | Fetch cross-frame tracked entities and recurrence profiles |
| `POST` | `/search` | Hybrid FTS5 text search + structured filters (location, severity) |
| `POST` | `/chat` | Conversational Security Analyst with dynamic tool execution |
| `GET` | `/summary` | **(Bonus)** Automated surveillance mission briefing |
| `POST` | `/pipeline/start` | Start background autonomous stream processing |
| `POST` | `/pipeline/stop` | Stop background autonomous stream processing |
| `GET` | `/pipeline/status`| Get current pipeline processing counts and intervals |

---

## 💡 Example API Requests & Responses

### 1. Hybrid Search (`POST /search`)
**Request:**
```json
{
  "query": "truck",
  "location": "Garage Loading Bay"
}
```
**Response:**
```json
{
  "query": "truck",
  "total_matches": 1,
  "results": [
    {
      "frame_id": "FRM-20260818-1200",
      "timestamp": "2026-08-18T12:00:00",
      "location": "Garage Loading Bay",
      "description": "A blue Ford F150 pickup truck backing into the primary delivery garage space.",
      "objects": [
        {
          "object_type": "vehicle",
          "label": "Ford F150",
          "attributes": {"color": "blue", "type": "pickup truck"},
          "confidence": 0.96
        }
      ],
      "activities": [
        {
          "activity_type": "entering",
          "confidence": 0.93,
          "notes": "Maneuvering into loading bay at Garage Loading Bay"
        }
      ],
      "risk_indicators": ["vehicle_loading_access"],
      "has_alert": false,
      "alert_severity": null,
      "rank_score": 0.6521
    }
  ]
}
```

### 2. Conversational Analyst (`POST /chat`)
**Request:**
```json
{
  "prompt": "How many times was the blue Ford truck observed today?"
}
```
**Response:**
```json
{
  "response": "The Ford F150 (blue) was observed 2 time(s) today. It was first spotted at 2026-08-18T12:00:00 at Garage Loading Bay, and subsequently tracked across Garage Loading Bay and later at Main Gate (last seen at 2026-08-18T14:30:00).",
  "intent": "vehicle_tracking",
  "tools_used": [
    {
      "tool_name": "get_events",
      "arguments": {"entity_type": "vehicle"},
      "result_summary": "Found 1 matching vehicle events."
    },
    {
      "tool_name": "search_frames",
      "arguments": {"query": "truck F150"},
      "result_summary": "Found 2 frames containing vehicle mentions."
    }
  ],
  "referenced_frames": ["FRM-20260818-1200", "FRM-20260818-1430"],
  "confidence": 0.96
}
```

---

## 🤝 AI-Assisted Co-Working Disclosure

In compliance with the FlytBase assignment evaluation requirements, this project was developed co-working with **Claude Code**, **Cursor AI**, **Windsurf**, and **Antigravity**. 
- See [`docs/ai_tool_log.md`](docs/ai_tool_log.md) for the full co-working log.
- See [`docs/demo_script.md`](docs/demo_script.md) for the 3–5 minute voiceover demo script.
- See [`design_report.md`](design_report.md) for the comprehensive 22-section architectural justification report.