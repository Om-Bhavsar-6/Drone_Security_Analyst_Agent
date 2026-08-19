import sqlite3
import os
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.core.logging import logger

SCHEMA_SQL = """
-- 1. Frames Table
CREATE TABLE IF NOT EXISTS frames (
    frame_id TEXT PRIMARY KEY,
    drone_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    location_tag TEXT NOT NULL,
    image_reference TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 2. Telemetry Table
CREATE TABLE IF NOT EXISTS telemetry (
    frame_id TEXT PRIMARY KEY,
    drone_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    altitude REAL NOT NULL,
    location_tag TEXT NOT NULL,
    battery_percentage REAL,
    heading_degrees REAL,
    speed_mps REAL,
    FOREIGN KEY(frame_id) REFERENCES frames(frame_id) ON DELETE CASCADE
);

-- 3. Observations Table
CREATE TABLE IF NOT EXISTS observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id TEXT NOT NULL,
    description TEXT NOT NULL,
    objects_json TEXT NOT NULL,
    activities_json TEXT NOT NULL,
    risk_indicators_json TEXT NOT NULL,
    vlm_confidence REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(frame_id) REFERENCES frames(frame_id) ON DELETE CASCADE
);

-- 4. Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    frame_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    location TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    severity TEXT NOT NULL,
    risk_score REAL NOT NULL,
    detection_confidence REAL NOT NULL,
    message TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    metadata_json TEXT,
    acknowledged INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(frame_id) REFERENCES frames(frame_id) ON DELETE CASCADE
);

-- 5. Tracked Events Table (Cross-Frame Aggregations)
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    entity_key TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    label TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    locations_json TEXT NOT NULL,
    frame_ids_json TEXT NOT NULL,
    activities_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    notes TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 6. SQLite FTS5 Virtual Table for Lexical Semantic Search
CREATE VIRTUAL TABLE IF NOT EXISTS fts_frames USING fts5(
    frame_id UNINDEXED,
    location,
    description,
    objects_text,
    activities_text,
    tokenize = 'porter unicode61'
);

-- Indices for rapid querying
CREATE INDEX IF NOT EXISTS idx_frames_timestamp ON frames(timestamp);
CREATE INDEX IF NOT EXISTS idx_frames_location ON frames(location_tag);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_events_entity_key ON events(entity_key);
"""

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self._ensure_dir()
        self.init_db()

    def _ensure_dir(self):
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        try:
            with self.get_connection() as conn:
                conn.executescript(SCHEMA_SQL)
                conn.commit()
            logger.info(f"Database initialized successfully at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

db = Database()
