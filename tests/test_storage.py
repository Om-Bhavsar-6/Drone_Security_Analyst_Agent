import pytest
from app.models.query import SearchRequest

def test_sqlite_persistence_and_fts_search(populated_test_env):
    frame_repo = populated_test_env["frame_repo"]
    retriever = populated_test_env["retriever"]
    
    assert frame_repo.get_frame_count() == 6
    
    # Test FTS5 query for "truck"
    res = retriever.search(SearchRequest(query="truck"))
    assert res.total_matches >= 2
    for item in res.results:
        assert "truck" in item.description.lower() or "f150" in item.description.lower()

    # Test FTS5 query for "deer"
    res_deer = retriever.search(SearchRequest(query="deer"))
    assert res_deer.total_matches == 1
    assert "deer" in res_deer.results[0].description.lower()
