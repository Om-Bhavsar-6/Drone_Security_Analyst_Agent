import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models.query import SearchRequest, SearchResultItem, SearchResponse
from app.storage.database import db, Database
from app.search.fts import FTSIndexer
from app.core.logging import logger

class HybridRetriever:
    def __init__(self, database: Database = db, fts_indexer: Optional[FTSIndexer] = None):
        self.database = database
        self.fts_indexer = fts_indexer or FTSIndexer(database)

    def search(self, req: SearchRequest) -> SearchResponse:
        """
        Performs hybrid retrieval:
        1. If text query is present, obtains ranked frame IDs from FTS5.
        2. Filters & enriches matching rows with structured telemetry, observations, and alert statuses.
        """
        fts_matches = {}
        if req.query and req.query.strip():
            fts_results = self.fts_indexer.search(req.query, limit=req.limit * 2)
            fts_matches = {item["frame_id"]: item["rank_score"] for item in fts_results}
            if not fts_matches:
                # No FTS matches found
                return SearchResponse(query=req.query, total_matches=0, results=[])

        query_sql = """
        SELECT 
            f.frame_id,
            f.timestamp,
            f.location_tag,
            o.description,
            o.objects_json,
            o.activities_json,
            o.risk_indicators_json,
            a.alert_id,
            a.severity as alert_severity
        FROM frames f
        LEFT JOIN observations o ON f.frame_id = o.frame_id
        LEFT JOIN alerts a ON f.frame_id = a.frame_id
        WHERE 1=1
        """
        params: List[Any] = []

        if fts_matches:
            placeholders = ",".join(["?"] * len(fts_matches))
            query_sql += f" AND f.frame_id IN ({placeholders})"
            params.extend(list(fts_matches.keys()))

        if req.location:
            query_sql += " AND LOWER(f.location_tag) LIKE ?"
            params.append(f"%{req.location.lower()}%")

        if req.start_time:
            query_sql += " AND f.timestamp >= ?"
            params.append(req.start_time.isoformat())

        if req.end_time:
            query_sql += " AND f.timestamp <= ?"
            params.append(req.end_time.isoformat())

        if req.min_severity:
            query_sql += " AND a.severity = ?"
            params.append(req.min_severity.value)

        query_sql += " ORDER BY f.timestamp ASC LIMIT ?"
        params.append(req.limit)

        with self.database.get_connection() as conn:
            rows = conn.execute(query_sql, params).fetchall()
            
            results: List[SearchResultItem] = []
            for r in rows:
                objects = json.loads(r["objects_json"]) if r["objects_json"] else []
                activities = json.loads(r["activities_json"]) if r["activities_json"] else []
                risk_indicators = json.loads(r["risk_indicators_json"]) if r["risk_indicators_json"] else []

                # Optional object_type filtering in structured metadata
                if req.object_type:
                    matched = any(o.get("object_type", "").lower() == req.object_type.lower() for o in objects)
                    if not matched:
                        continue

                results.append(
                    SearchResultItem(
                        frame_id=r["frame_id"],
                        timestamp=datetime.fromisoformat(r["timestamp"]),
                        location=r["location_tag"],
                        description=r["description"] or "",
                        objects=objects,
                        activities=activities,
                        risk_indicators=risk_indicators,
                        has_alert=bool(r["alert_id"]),
                        alert_severity=r["alert_severity"],
                        rank_score=fts_matches.get(r["frame_id"])
                    )
                )

            return SearchResponse(
                query=req.query,
                total_matches=len(results),
                results=results
            )

retriever = HybridRetriever()
