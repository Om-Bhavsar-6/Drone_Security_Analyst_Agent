# System Architecture: Autonomous Drone Security Analyst Agent

## 1. System Overview

The **Drone Security Analyst Agent** is a production-grade, multimodal autonomous security monitoring platform designed for docked security surveillance drones. The system continuously ingests synchronized aerial video frames and telemetry, generates dense structured observations using a Vision-Language Model (VLM) abstraction, persists frames into an SQLite database with an FTS5 full-text indexing engine, tracks multi-frame entity trajectories, evaluates context-driven heuristic security rules, and exposes an interactive tool-using conversational analyst.

---

## 2. Decoupled Architecture Diagram

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

## 3. Component Deep Dive

### A. Ingestion & Synchronization Layer (`app/pipeline/synchronizer.py`)
- **Idempotency**: Every frame is uniquely identified by `frame_id` (e.g. `FRM-20260818-0001`). Duplicate frames are rejected at the gate without duplicate database writes.
- **Clock Drift & Boundary Validation**: Validates GPS bounding boxes (Latitude -90 to +90, Longitude -180 to +180), verifies non-negative altitude, and flags desynchronization between telemetry clock and camera capture timestamp.

### B. Multimodal VLM Pipeline (`app/ai/`)
- **Structured Schema Extraction**: The VLM does not return arbitrary strings; it outputs strongly typed `StructuredObservation` models containing `objects`, `activities`, `risk_indicators`, and numerical `vlm_confidence`.
- **Pluggable Architecture**: Implements `BaseVLMEngine` with pluggable `MockVLMEngine` for deterministic testing and `GeminiVLMEngine` for real cloud multimodal inference.

### C. Persistent Storage & FTS5 Indexing (`app/storage/` & `app/search/`)
- **Durable Event Store**: Single-node SQLite relational database (`frames`, `telemetry`, `observations`, `alerts`, `events`).
- **FTS5 Lexical Search**: Virtual table `fts_frames` using Porter tokenizers and BM25 ranking algorithms for instant semantic text search across visual descriptions, detected entities, and zone tags.

### D. Cross-Frame Entity State Tracker (`app/detection/event_tracker.py`)
- Correlates entities over time (e.g., matching a Blue Ford F150 entering at 12:00 at the Garage and exiting at 14:30 at the Main Gate).
- Aggregates occurrence counts, visited locations, observed activities, and temporal timelines.

### E. Risk & Rule Engine (`app/detection/`)
- **Confidence vs Severity Decoupling**: VLM confidence (e.g., 0.95 confidence in vehicle detection) is mathematically decoupled from threat risk (e.g. authorized daytime delivery = LOW threat vs night perimeter loitering = HIGH threat).
- **Rules**:
  - `NightLoiteringRule`: Triggers on after-hours pedestrian loitering/pacing near restricted perimeters.
  - `RepeatedVehicleRule`: Cross-references multi-entry vehicle profiles against historical encounters.

### F. Security Analyst Conversational Agent (`app/agent/`)
- Dynamically selects forensic tools (`search_frames`, `get_events`, `get_alerts`, `get_timeline`, `get_statistics`) based on operator queries.
- Synthesizes timeline evidence into actionable security briefings.
