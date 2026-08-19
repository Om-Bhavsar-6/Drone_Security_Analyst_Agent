# AI-Assisted Development Log (FlytBase Co-Working Report)

This document transparently chronicles how modern AI development tools were leveraged to architect, code, refine, and test the **Drone Security Analyst Agent**, highlighting the division of labor between AI generation and human engineering oversight.

---

## 1. AI Tooling Summary Matrix

| Tool | Focus Area | AI Contribution | Human Engineering Review & Refinement |
|---|---|---|---|
| **Claude Code / Windsurf** | **Architecture & Scaffolding** | Generated initial FastAPI boilerplate and multi-module package layout (`app/`, `tests/`, `docs/`). | Enforced decoupled architecture, separated storage into SQLite + FTS5, replaced in-memory lists with persistent relational schema. |
| **Cursor / Antigravity** | **Domain Modeling & VLM Schema** | Drafted Pydantic domain models for telemetry, frames, and structured VLM observations. | Introduced `DetectedObject`, `DetectedActivity`, and `risk_indicators` schemas to eliminate unstructured string parsing in security rules. |
| **Windsurf / Cascade** | **Stateful Event Tracking & Rules** | Suggested heuristic condition logic for nighttime and recurrence rules. | Refactored detection into an isolated `RuleEngine`, added `SeverityScorer` to mathematically decouple model confidence from threat severity, and built the `EventTracker`. |
| **Claude Code** | **Hybrid Search & FTS5 Indexing** | Provided boilerplate SQLite FTS5 virtual table queries. | Added Porter tokenization, Unicode normalization, BM25 ranking adjustments, and combined structured SQL filtering with full-text search. |
| **Cursor AI** | **Security Analyst Agent** | Scaffolding for tool-using conversational assistant. | Replaced keyword branch matching with a tool-execution pattern (`search_frames`, `get_events`, `get_alerts`) returning traceable tool execution logs. |
| **Antigravity CLI** | **Automated QA & Test Suite** | Generated initial unit test templates. | Implemented 19 rigorous tests covering edge cases: clock desync, duplicate frame rejection, out-of-bound altitudes, and API contract validations. |

---

## 2. Detailed Work Breakdown & Iteration Notes

### Step 1: Moving from In-Memory State to Durable Persistence
- **Initial AI Draft**: The initial prototype scaffolded by AI stored frames in global lists `indexed_database: List[Dict]`.
- **Engineering Decision**: Identified that in-memory storage loses state across restarts and breaks temporal cross-frame context. Engineered a persistent SQLite schema with ACID transaction safety and an FTS5 virtual table for lexical semantic queries.

### Step 2: Structured VLM Observation vs Raw String Output
- **Initial AI Draft**: VLM mocked outputs were simple strings like `"A lone individual in a dark hoodie pacing back and forth near the fence line."`
- **Engineering Decision**: Prompted AI to generate a strongly typed `StructuredObservation` schema. Security rules now inspect structured attributes (`objects.type == "person"`, `activities.type == "loitering"`) instead of brittle substring matches.

### Step 3: Decoupling Model Confidence from Threat Severity
- **Initial AI Draft**: Rules assigned static string severities (`"High"`).
- **Engineering Decision**: Designed `SeverityScorer` which dynamically factors in time-of-day, location sensitivity, loitering persistence, and visual risk indicators while preserving the VLM's independent visual confidence score.

### Step 4: Cross-Frame Entity Disambiguation
- **Initial AI Draft**: Each frame was evaluated independently.
- **Engineering Decision**: Created `EventTracker` to correlate entity fingerprints across time, enabling multi-entry tracking (e.g. Blue Ford F150 seen at 12:00 and 14:30).

---

## 3. Key Takeaway on AI-Assisted Engineering

Pair-programming with AI tools accelerated boilerplate generation, schema definition, and test authoring by an estimated **4x to 5x**. The engineer's role shifted to high-leverage architectural governance: verifying production reliability, establishing clean boundary abstractions, enforcing data durability, and ensuring mathematical correctness in risk evaluation.
