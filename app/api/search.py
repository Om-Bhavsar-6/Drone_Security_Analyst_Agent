from fastapi import APIRouter
from app.models.query import SearchRequest, SearchResponse
from app.search.retriever import retriever

router = APIRouter(tags=["Search & Indexing"])

@router.post("/search", response_model=SearchResponse)
def search_indexed_frames(payload: SearchRequest):
    """
    Search indexed frames using hybrid SQLite FTS5 full-text search
    and structured metadata filtering (location, time, severity, object_type).
    """
    return retriever.search(payload)
