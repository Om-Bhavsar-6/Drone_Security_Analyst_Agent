# 🎬 FlytBase Video Demo Handover Playbook & Voiceover Script
**Candidate**: Om Bhavsar — AI Engineer Candidate  
**Project**: Autonomous Drone Security Analyst Agent  
**Target Video Duration**: 4–5 Minutes (or split into individual goal clips)  

---

## 📋 Recording Checklist Before You Start

1. **Terminal 1**: Start the NiceGUI Dashboard:
   ```bash
   cd drone_security_agent
   python dashboard.py
   ```
2. **Terminal 2**: Start the FastAPI Server:
   ```bash
   cd drone_security_agent
   python -m uvicorn app.main:app --port 8000
   ```
3. **Browser Tabs Prepared**:
   - Tab 1: **NiceGUI SOC Dashboard**: `http://localhost:8080`
   - Tab 2: **FastAPI Swagger Docs**: `http://localhost:8000/docs`
   - Tab 3: **Architecture Diagram**: Open [`docs/architecture.md`](architecture.md) in your IDE or browser
   - Tab 4: **Rendered Frame Images**: Open folder `data/rendered_frames/` or view in IDE

---

## ⏱️ Video Structure & Step-by-Step Action Guide

```
┌───────────────────────────┬───────────────────────────┬───────────────────────────┐
│ Segment / Goal            │ Screen Action / What to Show│ Voiceover Duration        │
├───────────────────────────┼───────────────────────────┼───────────────────────────┤
│ 1. Intro & Architecture   │ Architecture Diagram      │ 00:00 – 00:45 (45s)       │
│ 2. Video Processing & VLM │ NiceGUI Dashboard + HUD   │ 00:45 – 01:45 (60s)       │
│ 3. Context & Event Tracker│ Entity Matrix + OpenCV    │ 01:45 – 02:45 (60s)       │
│ 4. Search & Agent QA      │ FTS5 Search + Chat Assistant│ 02:45 – 03:45 (60s)     │
│ 5. Scalability & QA Tests │ Terminal pytest execution │ 03:45 – 04:30 (45s)       │
│ 6. Conclusion & Handover  │ Swagger /summary + Report │ 04:30 – 05:00 (30s)       │
└───────────────────────────┴───────────────────────────┴───────────────────────────┘
```

---

## 🎙️ Complete Word-for-Word Voiceover Script

### 🟢 Goal 1: Introduction & Architecture (00:00 – 00:45)
**Screen Action**:
- Show the System Architecture Diagram from `docs/architecture.md` on screen.
- Highlight the decoupled pipeline (Drone Ingestion $\to$ Synchronizer $\to$ VLM $\to$ SQLite+FTS5 $\to$ Rule Engine $\to$ Agent).

**Your Voiceover**:
> *"Hello FlytBase team! My name is Om Bhavsar, and today I'm demonstrating the production-grade Autonomous Drone Security Analyst Agent. 
> 
> Docked security drones capture continuous aerial video over industrial facilities, generating immense volumes of unstructured video and telemetry that overwhelm security guards. 
> 
> To solve this without false-alarm fatigue, I engineered a decoupled, multimodal system:
> 1. Real-time telemetry is validated and synchronized with frame timestamps using an idempotent ingestion gate.
> 2. A Vision-Language Model produces strongly-typed structured observations rather than brittle text.
> 3. Persistent SQLite with an FTS5 virtual table provides sub-millisecond lexical search.
> 4. A stateful Event Tracker correlates entities across time and space.
> 5. A multi-factor risk engine decouples model confidence from threat severity.
> 6. And dual conversational agents—both a sub-5ms native agent and a LangChain enterprise toolkit—enable natural language forensic investigation.
> 
> Let’s jump into the live operations center!"*

---

### 🟢 Goal 2: Video Processing & Real-Time Alert Engine (00:45 – 01:45)
**Screen Action**:
- Switch to browser at `http://localhost:8080` (NiceGUI Dashboard).
- Click the **"Step Frame"** button or **"Start Patrol"**.
- Watch the live telemetry HUD update (Location: `Main Gate`, Altitude: `15.0m`, GPS: `18.5204° N, 73.8567° E`).
- Point out the VLM inference latency (`VLM: 0.1ms`), FTS5 index time (`Index: 12ms`), and rule evaluation time.
- Point to the **Security Threat Incidents** panel on the right where the **`[CRITICAL] Nighttime Perimeter Loitering Detection`** alert appears.

**Your Voiceover**:
> *"Here in our Security Operations Center dashboard, we can see live drone telemetry streaming in real time. 
> 
> As I step through the surveillance feed, each frame is processed through our multimodal pipeline. 
> 
> Notice Frame 1 at 00:01 at the Main Gate: The VLM detects an adult individual in a dark hoodie pacing near the fence line. Our Rule Engine combines the temporal night context—between 22:00 and 05:00—with restricted perimeter indicators. 
> 
> Rather than relying on simple string matching, our Severity Scorer computes a weighted risk score of 0.85, immediately generating a CRITICAL alert with an actionable dispatch protocol: 'Dispatch ground security team to intercept individual and verify credentials'."*

---

### 🟢 Goal 3: Cross-Frame Context & OpenCV Frame Generation (01:45 – 02:45)
**Screen Action**:
- In the NiceGUI Dashboard, scroll to the **"Cross-Frame Entity Recurrence Matrix"**.
- Show the card for **`Ford F150 (blue)`** showing **2 Sightings** and Trajectory: `Garage Loading Bay ➔ Main Gate`.
- Show the card for **`Adult Individual (dark hoodie)`** showing **3 Sightings**.
- Open the folder `data/rendered_frames/` and open `FRM-20260818-1200.jpg` or `FRM-20260818-0001.jpg` to show the OpenCV HUD overlay and color-coded bounding boxes.

**Your Voiceover**:
> *"Single-frame analysis cannot tell if a vehicle is routine or suspicious. That's where our cross-frame reasoning comes in. 
> 
> At 12:00, a Blue Ford F150 was spotted backing into the Garage Loading Bay. Later at 14:30, the same vehicle was observed exiting through the Main Gate. 
> 
> Our stateful Event Tracker generates composite entity fingerprints, automatically linking the two frames, updating the occurrence count to 2, and tracking its spatial trajectory across zones.
> 
> Furthermore, using OpenCV, we burn real-time telemetry HUD overlays—including GPS coordinates, altitude, battery percentage, and color-coded entity bounding boxes—directly onto each optical frame canvas, saving rendered evidence into our local storage for visual forensics."*

---

### 🟢 Goal 4: Hybrid FTS5 Search & Tool-Using Analyst Agent (02:45 – 03:45)
**Screen Action**:
- Scroll down to the **"Hybrid FTS5 Forensic Search Studio"** in the dashboard.
- Type `"truck"` into the search box and click **"Search Frames"**. Show the instant sub-millisecond BM25 ranked matches.
- Change location filter to `"Garage Loading Bay"` and search again.
- Scroll back up to the **"AI Security Analyst Assistant"** chat window.
- Click the quick chip: **`"Blue Truck?"`** (or type: *"How many times was the blue Ford truck observed today?"*) and press Send.
- Point out the response text, the executed tools (`get_events`, `search_frames`), confidence (`96%`), and referenced frame IDs (`FRM-20260818-1200`, `FRM-20260818-1430`).
- Click the quick chip: **`"Loitering?"`** and show the night security briefing.

**Your Voiceover**:
> *"For rapid forensic retrieval, we implemented SQLite FTS5 with Porter tokenization and BM25 ranking. When I search for 'truck', it returns matching frames enriched with metadata in under 2 milliseconds.
> 
> For operational handover, security commanders can chat naturally with our Security Analyst Assistant. 
> 
> Rather than simple keyword matching, the assistant dynamically selects domain tools. When I ask: 'How many times was the blue Ford truck observed today?', the agent invokes `get_events` and `search_frames`, synthesizing the full timeline: the truck was spotted twice, first at the Garage at 12:00 and last seen at the Main Gate at 14:30.
> 
> It also provides standard LangChain `@tool` definitions in `app/agent/langchain_agent.py` for enterprise orchestration."*

---

### 🟢 Goal 5: Scalability & Automated QA Test Suite (03:45 – 04:30)
**Screen Action**:
- Switch to the terminal in `drone_security_agent`.
- Run: `python -m pytest`
- Let the 21 passing test cases execute and show the green `21 passed in 4.27s` output on screen.
- Mention edge cases tested (clock drift, duplicate frame idempotency, boundary checks, LangChain toolkit).

**Your Voiceover**:
> *"To ensure enterprise-grade reliability, the entire platform is backed by an automated test suite of 21 tests covering unit, integration, API contracts, and failure resilience.
> 
> As you can see, our tests validate clock drift desynchronization, duplicate frame idempotency—preventing re-indexing if a drone retransmits packets—and GPS boundary validation with a 100% pass rate."*

---

### 🟢 Goal 6: Shift Summary & Handover Conclusion (04:30 – 05:00)
**Screen Action**:
- Switch to `http://localhost:8000/docs` (Swagger UI).
- Open `GET /summary` and click **"Try it out" $\to$ "Execute"**.
- Show the JSON response containing the mission briefing, total analyzed frames, and active alerts.
- Show the compiled PDF report `FlytBase_AI_Engineer_Design_Report_Om_Bhavsar.pdf`.

**Your Voiceover**:
> *"Finally, our `/summary` endpoint provides an automated mission briefing aggregating all flight telemetry, alerts, and entity counts into an executive report.
> 
> All source code, the 17-section architectural report in PDF, OpenCV rendering engine, NiceGUI dashboard, and setup instructions are submitted in the private repository with `assignments@flytbase.com` added as a contributor.
> 
> Thank you for your time, and I look forward to discussing how I can contribute to the AI engineering team at FlytBase!"*
