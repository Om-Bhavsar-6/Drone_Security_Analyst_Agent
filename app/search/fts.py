import re
from typing import List, Dict, Any, Tuple
from app.storage.database import db, Database
from app.core.logging import logger

class FTSIndexer:
    def __init__(self, database: Database = db):
        self.database = database

    def search(self, query_text: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Executes an FTS5 full-text search query across descriptions, objects, and activities.
        Uses BM25 ranking and wildcard suffix support.
        """
        if not query_text or not query_text.strip():
            return []

        # Sanitize query tokens for FTS5 syntax
        clean_tokens = re.findall(r"\w+", query_text.strip())
        if not clean_tokens:
            return []

        # Format FTS5 query: token1* OR token2* OR "token1 token2"
        fts_query = " OR ".join([f'"{tok}"*' for tok in clean_tokens])

        sql = """
        SELECT 
            fts.frame_id,
            fts.location,
            fts.description,
            bm25(fts_frames) AS rank_score
        FROM fts_frames fts
        WHERE fts_frames MATCH ?
        ORDER BY rank_score ASC
        LIMIT ?;
        """

        with self.database.get_connection() as conn:
            try:
                rows = conn.execute(sql, (fts_query, limit)).fetchall()
                results = []
                for r in rows:
                    results.append({
                        "frame_id": r["frame_id"],
                        "location": r["location"],
                        "description": r["description"],
                        "rank_score": round(abs(float(r["rank_score"])), 4)
                    })
                return results
            except Exception as e:
                logger.error(f"FTS5 Query failed: '{fts_query}' -> {e}")
                return []
