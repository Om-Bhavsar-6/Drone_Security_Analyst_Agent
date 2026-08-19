import sqlite3
from typing import List, Dict, Any

class FrameIndexer:
    def __init__(self, db_path: str = "frames.db"):
        """Initialize the SQLite database with FTS5 index."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create the frames table and FTS5 index."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Create the main table to store all frame data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS frames (
                    id INTEGER PRIMARY KEY,
                    description TEXT,
                    location TEXT,
                    timestamp TEXT,
                    lat REAL,
                    lon REAL,
                    alt REAL
                )
            """)
            # Create the FTS5 virtual table for full-text search on description and location
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS frames_fts
                USING fts5(
                    description,
                    location,
                    content='frames',
                    content_rowid='id'
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def add_frame(self, frame_data: Dict[str, Any]) -> None:
        """Add a frame with metadata to the database and update FTS5 index."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                INSERT INTO frames
                (description, location, timestamp, lat, lon, alt)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                frame_data.get("description", ""),
                frame_data.get("location", ""),
                frame_data.get("timestamp", ""),
                frame_data.get("telemetry", {}).get("lat", 0.0),
                frame_data.get("telemetry", {}).get("lon", 0.0),
                frame_data.get("telemetry", {}).get("alt", 0.0)
            ))
            frame_id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

    def search_by_text(self, query: str) -> List[Dict[str, Any]]:
        """Search frames using FTS5 MATCH query and return matching frames with metadata."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Use FTS5 to find matching rowids, then join with frames table to get full data
            cursor = conn.execute("""
                SELECT f.id, f.description, f.location, f.timestamp, f.lat, f.lon, f.alt
                FROM frames f
                INNER JOIN frames_fts ON f.id = frames_fts.rowid
                WHERE frames_fts MATCH ?
            """, (query,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "description": row[1],
                    "location": row[2],
                    "timestamp": row[3],
                    "telemetry": {
                        "lat": row[4],
                        "lon": row[5],
                        "alt": row[6]
                    }
                })
            return results
        finally:
            conn.close()

    def get_all(self) -> List[Dict[str, Any]]:
        """Retrieve all frames from the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT id, description, location, timestamp, lat, lon, alt
                FROM frames
                ORDER BY id
            """)

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "description": row[1],
                    "location": row[2],
                    "timestamp": row[3],
                    "telemetry": {
                        "lat": row[4],
                        "lon": row[5],
                        "alt": row[6]
                    }
                })
            return results
        finally:
            conn.close()

    def clear(self) -> None:
        """Clear all frames from the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("DELETE FROM frames")
            conn.commit()
        finally:
            conn.close()

# Global indexer instance
indexer = FrameIndexer()