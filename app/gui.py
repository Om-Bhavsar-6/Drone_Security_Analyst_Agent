from nicegui import ui, app
import asyncio
from datetime import datetime
from typing import List, Dict, Any

from app.storage.repositories import FrameRepository, AlertRepository, EventRepository
from app.search.retriever import retriever
from app.agent.assistant import security_assistant
from app.models.query import SearchRequest, ChatRequest
from app.pipeline.orchestrator import pipeline_manager
from app.pipeline.simulator import generate_simulated_packets
from app.pipeline.processor import frame_processor

def init_gui():
    frame_repo = FrameRepository()
    alert_repo = AlertRepository()
    event_repo = EventRepository()

    @ui.page("/")
    def dashboard_page():
        # Apply dark mode & high-tech styling
        ui.dark_mode().enable()
        ui.add_head_html("""
            <style>
                body { font-family: 'Inter', -apple-system, sans-serif; background-color: #0b0f19; }
                .soc-card { background: rgba(18, 24, 38, 0.85); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; }
                .glow-blue { box-shadow: 0 0 15px rgba(59, 130, 246, 0.25); }
                .glow-red { box-shadow: 0 0 15px rgba(239, 68, 68, 0.35); }
                .hud-stat { font-family: 'JetBrains Mono', monospace; }
            </style>
        """)

        with ui.header().classes("bg-slate-900 border-b border-slate-800 text-white px-6 py-3 items-center justify-between"):
            with ui.row().classes("items-center gap-3"):
                ui.icon("radar", size="md", color="cyan-400").classes("animate-spin")
                with ui.column().classes("gap-0"):
                    ui.label("DRONE SECURITY ANALYST AGENT").classes("text-lg font-bold tracking-wider text-cyan-400")
                    ui.label("Autonomous Multimodal Aerial Surveillance & Forensic Operations").classes("text-xs text-slate-400")
            
            with ui.row().classes("items-center gap-4"):
                pipeline_status_badge = ui.badge("STREAM READY", color="teal-700").classes("px-3 py-1 font-mono text-xs")
                ui.button("API Docs", on_click=lambda: ui.navigate.to("/docs"), icon="api").props("outline dense color=cyan")

        with ui.column().classes("w-full max-w-7xl mx-auto p-6 gap-6"):
            
            # --- TOP KPI METRICS ROW ---
            with ui.row().classes("w-full grid grid-cols-1 md:grid-cols-4 gap-4"):
                with ui.card().classes("soc-card p-4 items-center"):
                    ui.label("INGESTED FRAMES").classes("text-xs text-slate-400 font-semibold tracking-wider")
                    total_frames_label = ui.label("0").classes("hud-stat text-3xl font-bold text-cyan-400")
                
                with ui.card().classes("soc-card p-4 items-center"):
                    ui.label("ACTIVE ALERTS").classes("text-xs text-slate-400 font-semibold tracking-wider")
                    total_alerts_label = ui.label("0").classes("hud-stat text-3xl font-bold text-red-400")

                with ui.card().classes("soc-card p-4 items-center"):
                    ui.label("TRACKED ENTITIES").classes("text-xs text-slate-400 font-semibold tracking-wider")
                    total_events_label = ui.label("0").classes("hud-stat text-3xl font-bold text-amber-400")

                with ui.card().classes("soc-card p-4 items-center"):
                    ui.label("SYSTEM INTEGRITY").classes("text-xs text-slate-400 font-semibold tracking-wider")
                    ui.label("100% NOMINAL").classes("hud-stat text-3xl font-bold text-emerald-400")

            # --- MAIN TWO-COLUMN DASHBOARD ---
            with ui.row().classes("w-full grid grid-cols-1 lg:grid-cols-12 gap-6"):
                
                # LEFT COLUMN: Live Drone Telemetry & Mission Feed (7 cols)
                with ui.column().classes("lg:col-span-7 gap-6"):
                    
                    # 1. Telemetry HUD & Controls
                    with ui.card().classes("soc-card p-5 w-full"):
                        with ui.row().classes("w-full justify-between items-center mb-2"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("flight_takeoff", color="cyan-400")
                                ui.label("SURVEILLANCE FLIGHT CONTROLLER").classes("font-bold text-slate-200")
                            
                            with ui.row().classes("gap-2"):
                                start_btn = ui.button("Start Patrol", icon="play_arrow").props("dense color=cyan-7")
                                stop_btn = ui.button("Stop Patrol", icon="stop").props("dense color=slate-7")
                                ingest_btn = ui.button("Step Frame", icon="skip_next").props("dense color=indigo-7")

                        # Live HUD Strip
                        with ui.row().classes("w-full bg-slate-950 p-3 rounded-lg border border-slate-800 justify-between items-center text-xs hud-stat text-slate-300"):
                            with ui.column().classes("gap-0"):
                                ui.label("DRONE ID").classes("text-slate-500 text-[10px]")
                                ui.label("DRONE-01").classes("text-cyan-400 font-bold")
                            with ui.column().classes("gap-0"):
                                ui.label("LOCATION").classes("text-slate-500 text-[10px]")
                                hud_loc = ui.label("Main Gate").classes("text-slate-200")
                            with ui.column().classes("gap-0"):
                                ui.label("ALTITUDE").classes("text-slate-500 text-[10px]")
                                hud_alt = ui.label("15.0m").classes("text-emerald-400")
                            with ui.column().classes("gap-0"):
                                ui.label("COORDINATES").classes("text-slate-500 text-[10px]")
                                hud_gps = ui.label("18.5204° N, 73.8567° E").classes("text-slate-300")
                            with ui.column().classes("gap-0"):
                                ui.label("BATTERY").classes("text-slate-500 text-[10px]")
                                ui.label("95%").classes("text-teal-400")

                        # Live Camera Viewport Simulation
                        with ui.card().classes("w-full mt-4 bg-slate-950 border border-slate-800 p-4 rounded-lg relative overflow-hidden"):
                            ui.label("🔴 LIVE OPTICAL FEED").classes("text-[10px] text-red-500 font-mono tracking-widest")
                            current_frame_title = ui.label("Awaiting stream packet...").classes("text-sm font-semibold text-slate-100 mt-1")
                            current_frame_desc = ui.label("Start patrol or step frame to run VLM feature extraction.").classes("text-xs text-slate-400 mt-1 italic")
                            
                            with ui.row().classes("mt-3 gap-2"):
                                vlm_badge = ui.badge("VLM: READY", color="slate-800").classes("text-[10px] font-mono")
                                index_badge = ui.badge("FTS5: READY", color="slate-800").classes("text-[10px] font-mono")
                                alert_badge = ui.badge("RULES: ACTIVE", color="slate-800").classes("text-[10px] font-mono")

                    # 2. Stateful Tracked Entities & Trajectory Matrix
                    with ui.card().classes("soc-card p-5 w-full"):
                        with ui.row().classes("items-center gap-2 mb-3"):
                            ui.icon("hub", color="amber-400")
                            ui.label("CROSS-FRAME ENTITY RECURRENCE MATRIX").classes("font-bold text-slate-200")
                        
                        entities_container = ui.column().classes("w-full gap-2")

                # RIGHT COLUMN: Security Alerts & Forensic Analyst Chat (5 cols)
                with ui.column().classes("lg:col-span-5 gap-6"):
                    
                    # 1. Real-Time Alert Ticker
                    with ui.card().classes("soc-card p-5 w-full"):
                        with ui.row().classes("items-center justify-between mb-3"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("warning", color="red-400")
                                ui.label("SECURITY THREAT INCIDENTS").classes("font-bold text-slate-200")
                            alert_count_badge = ui.badge("0 ALERTS", color="red-900").classes("text-[10px] font-mono")
                        
                        alerts_container = ui.column().classes("w-full gap-3 max-h-64 overflow-y-auto pr-1")

                    # 2. Conversational Security Analyst Agent
                    with ui.card().classes("soc-card p-5 w-full flex flex-col"):
                        with ui.row().classes("items-center gap-2 mb-2"):
                            ui.icon("psychology", color="cyan-400")
                            ui.label("AI SECURITY ANALYST ASSISTANT").classes("font-bold text-slate-200")
                        
                        chat_log = ui.column().classes("w-full gap-3 p-3 bg-slate-950 rounded-lg border border-slate-800 max-h-80 overflow-y-auto mb-3")
                        
                        # Pre-populate greeting
                        with chat_log:
                            with ui.chat_message(name="Analyst Agent", sent=False, stamp="🤖 AI Analyst").classes("text-xs"):
                                ui.markdown("Hello Commander. I am monitoring the drone telemetry and VLM stream. Ask me anything regarding vehicle trajectories, suspicious loitering, or shift summaries.")

                        with ui.row().classes("w-full gap-2"):
                            chat_input = ui.input(placeholder="e.g. How many times did the blue truck enter today?").classes("flex-grow").props("dense outlined")
                            send_btn = ui.button(icon="send").props("dense color=cyan-7")

                        # Sample quick query chips
                        with ui.row().classes("w-full gap-1 mt-2"):
                            ui.chip("Blue Truck?", on_click=lambda: set_chat_input("How many times was the blue Ford truck observed today?")).classes("text-[10px]")
                            ui.chip("Loitering?", on_click=lambda: set_chat_input("Was anyone loitering near the main gate at night?")).classes("text-[10px]")
                            ui.chip("Shift Summary", on_click=lambda: set_chat_input("Give me a summary of all activity today.")).classes("text-[10px]")

            # --- BOTTOM ROW: Hybrid FTS5 Forensic Search Studio ---
            with ui.card().classes("soc-card p-5 w-full"):
                with ui.row().classes("items-center justify-between mb-4"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("manage_search", color="cyan-400")
                        ui.label("HYBRID FTS5 FORENSIC SEARCH STUDIO").classes("font-bold text-slate-200")
                    ui.label("SQLite FTS5 + BM25 Lexical Ranking").classes("text-xs text-slate-400 font-mono")

                with ui.row().classes("w-full gap-3 mb-4"):
                    search_input = ui.input(placeholder="Enter search tokens (e.g. truck, deer, hoodie, gate)...").classes("flex-grow").props("dense outlined")
                    loc_filter = ui.select(["All Locations", "Main Gate", "Garage Loading Bay", "North Perimeter"], value="All Locations").classes("w-48").props("dense outlined")
                    search_btn = ui.button("Search Frames", icon="search").props("dense color=cyan-7")

                search_results_container = ui.column().classes("w-full gap-2")

        # --- UI UPDATE & INTERACTION LOGIC ---
        
        def set_chat_input(text: str):
            chat_input.value = text

        def refresh_stats():
            total_frames_label.text = str(frame_repo.get_frame_count())
            total_alerts_label.text = str(alert_repo.get_alert_count())
            total_events_label.text = str(len(event_repo.get_all_events()))
            alert_count_badge.text = f"{alert_repo.get_alert_count()} ALERTS"

        def refresh_alerts():
            alerts_container.clear()
            alerts = alert_repo.get_all_alerts()
            if not alerts:
                with alerts_container:
                    ui.label("No active security violations detected.").classes("text-xs text-slate-500 italic")
                return

            with alerts_container:
                for a in alerts:
                    sev = a.get("severity", "LOW")
                    border_col = "border-red-600 bg-red-950/30" if sev in ["CRITICAL", "HIGH"] else "border-amber-600 bg-amber-950/30"
                    with ui.card().classes(f"w-full p-3 rounded-lg border {border_col}"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.badge(f"[{sev}] {a.get('rule_name')}", color="red-7" if sev in ["CRITICAL", "HIGH"] else "amber-7").classes("text-[10px] font-mono")
                            ui.label(a.get("timestamp", "")[11:19]).classes("text-[10px] text-slate-400 font-mono")
                        ui.label(a.get("message", "")).classes("text-xs font-semibold text-slate-100 mt-1")
                        ui.label(f"Action: {a.get('recommended_action', '')}").classes("text-[11px] text-slate-400 mt-1")

        def refresh_events():
            entities_container.clear()
            events = event_repo.get_all_events()
            if not events:
                with entities_container:
                    ui.label("No multi-frame entity profiles registered yet.").classes("text-xs text-slate-500 italic")
                return

            with entities_container:
                for e in events:
                    with ui.card().classes("w-full p-3 rounded-lg bg-slate-950 border border-slate-800"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("directions_car" if e.entity_type == "vehicle" else "person", color="cyan-400", size="xs")
                                ui.label(e.label).classes("text-xs font-bold text-slate-200")
                            ui.badge(f"{e.occurrence_count} Sighting(s)", color="teal-8").classes("text-[10px] font-mono")
                        
                        loc_str = " ➔ ".join(e.locations)
                        ui.label(f"Trajectory: {loc_str}").classes("text-[11px] text-slate-400 mt-1")
                        ui.label(f"Timeline: First seen {e.first_seen.strftime('%H:%M')} | Last seen {e.last_seen.strftime('%H:%M')}").classes("text-[10px] text-slate-500 font-mono")

        async def run_search():
            search_results_container.clear()
            q = search_input.value or ""
            loc = loc_filter.value if loc_filter.value != "All Locations" else None
            
            res = retriever.search(SearchRequest(query=q, location=loc, limit=10))
            
            with search_results_container:
                ui.label(f"Query returned {res.total_matches} frame(s)").classes("text-xs text-slate-400 font-mono mb-2")
                if not res.results:
                    ui.label("No matching frames found.").classes("text-xs text-slate-500 italic")
                    return

                for item in res.results:
                    with ui.card().classes("w-full p-3 rounded-lg bg-slate-950 border border-slate-800"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-2"):
                                ui.badge(item.frame_id, color="slate-800").classes("text-[10px] font-mono")
                                ui.label(f"@ {item.location} ({item.timestamp.strftime('%H:%M:%S')})").classes("text-xs font-bold text-cyan-300")
                            if item.has_alert:
                                ui.badge(f"ALERT: {item.alert_severity}", color="red-8").classes("text-[10px] font-mono")
                        
                        ui.label(item.description).classes("text-xs text-slate-200 mt-1")
                        
                        if item.objects:
                            with ui.row().classes("gap-1 mt-2"):
                                for obj in item.objects:
                                    ui.chip(f"{obj.get('label')} ({int(obj.get('confidence', 0)*100)}%)").classes("text-[9px] bg-slate-800")

        async def send_chat():
            prompt = chat_input.value
            if not prompt or not prompt.strip():
                return
            
            chat_input.value = ""
            
            with chat_log:
                with ui.chat_message(name="Operator", sent=True).classes("text-xs"):
                    ui.label(prompt)
            
            resp = security_assistant.process_query(ChatRequest(prompt=prompt))
            
            with chat_log:
                with ui.chat_message(name="Analyst Agent", sent=False, stamp="🤖 AI Analyst").classes("text-xs"):
                    ui.markdown(resp.response)
                    if resp.tools_used:
                        tools_str = ", ".join([t.tool_name for t in resp.tools_used])
                        ui.label(f"🛠️ Tools: {tools_str} | Confidence: {int(resp.confidence*100)}%").classes("text-[10px] text-slate-400 font-mono mt-1")
                    if resp.referenced_frames:
                        ui.label(f"📎 Frames: {', '.join(resp.referenced_frames)}").classes("text-[10px] text-cyan-400 font-mono")

        # Ingest single frame step
        async def step_single_frame():
            packets = generate_simulated_packets()
            current_count = frame_repo.get_frame_count()
            packet_to_ingest = packets[current_count % len(packets)]
            
            res = frame_processor.process_frame(packet_to_ingest)
            
            hud_loc.text = packet_to_ingest.telemetry.location_tag
            hud_alt.text = f"{packet_to_ingest.telemetry.altitude}m"
            hud_gps.text = f"{packet_to_ingest.telemetry.latitude}° N, {packet_to_ingest.telemetry.longitude}° E"
            
            current_frame_title.text = f"Frame {packet_to_ingest.frame_id} @ {packet_to_ingest.telemetry.location_tag} [{packet_to_ingest.timestamp.strftime('%H:%M:%S')}]"
            
            if res.get("status") == "success":
                current_frame_desc.text = res["observation"]["description"]
                vlm_badge.text = f"VLM: {res['metrics_ms']['vlm']}ms"
                index_badge.text = f"FTS5: {res['metrics_ms']['indexing']}ms"
                alert_badge.text = f"RULES: {res['metrics_ms']['rules']}ms"
                ui.notify(f"Ingested Frame {packet_to_ingest.frame_id}", type="positive")
            else:
                existing_frame = frame_repo.get_frame(packet_to_ingest.frame_id)
                current_frame_desc.text = existing_frame.get("description", "Frame already indexed in database.") if existing_frame else res.get("message", "Frame processed.")
                ui.notify(f"Frame {packet_to_ingest.frame_id} (Already Indexed)", type="info")
            
            refresh_stats()
            refresh_alerts()
            refresh_events()

        async def start_patrol():
            pipeline_status_badge.text = "PATROL STREAMING"
            pipeline_status_badge.props("color=cyan-7")
            await pipeline_manager.start_pipeline()
            ui.notify("Autonomous drone surveillance patrol started", type="info")

        async def stop_patrol():
            pipeline_status_badge.text = "STREAM PAUSED"
            pipeline_status_badge.props("color=slate-7")
            await pipeline_manager.stop_pipeline()
            refresh_stats()
            refresh_alerts()
            refresh_events()
            ui.notify("Patrol paused", type="warning")

        # Attach event handlers
        start_btn.on_click(start_patrol)
        stop_btn.on_click(stop_patrol)
        ingest_btn.on_click(step_single_frame)
        search_btn.on_click(run_search)
        send_btn.on_click(send_chat)
        chat_input.on('keydown.enter', send_chat)

        # Initial data loading
        refresh_stats()
        refresh_alerts()
        refresh_events()

        # Periodic background UI sync timer
        ui.timer(2.0, lambda: [refresh_stats(), refresh_alerts(), refresh_events()])
