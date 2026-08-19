import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def api_client():
    with TestClient(app) as client:
        yield client

def test_api_health(api_client):
    res = api_client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "total_frames_indexed" in data

def test_api_logs(api_client):
    res = api_client.get("/logs")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert isinstance(data["data"], list)

def test_api_alerts(api_client):
    res = api_client.get("/alerts")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert isinstance(data["alerts"], list)

def test_api_search(api_client):
    res = api_client.post("/search", json={"query": "truck"})
    assert res.status_code == 200
    data = res.json()
    assert "total_matches" in data
    assert "results" in data

def test_api_chat(api_client):
    res = api_client.post("/chat", json={"prompt": "What happened with the blue truck?"})
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert "intent" in data
    assert "tools_used" in data

def test_api_summary(api_client):
    res = api_client.get("/summary")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "total_frames_analyzed" in data
