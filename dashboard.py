"""
Standalone launcher for the NiceGUI Drone Security Operations Center Dashboard.
"""
from nicegui import ui
from app.gui import init_gui
from app.storage.database import db

if __name__ in {"__main__", "__mp_main__"}:
    db.init_db()
    init_gui()
    print("[DRONE SOC] Launching Drone Security Analyst SOC Dashboard on http://localhost:8080 ...")
    ui.run(
        port=8080,
        title="Drone Security Analyst SOC",
        reload=False,
        show=False,
    )
