import pytest
import os
from fastapi.testclient import TestClient
from app.storage.database import Database
from app.storage.repositories import FrameRepository, ObservationRepository, AlertRepository, EventRepository
from app.search.fts import FTSIndexer
from app.search.retriever import HybridRetriever
from app.pipeline.processor import FrameProcessor
from app.pipeline.simulator import generate_simulated_packets
from app.main import app

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_drone.db"
    db_instance = Database(str(db_file))
    return db_instance

@pytest.fixture
def test_repos(test_db):
    frame_repo = FrameRepository(test_db)
    obs_repo = ObservationRepository(test_db)
    alert_repo = AlertRepository(test_db)
    event_repo = EventRepository(test_db)
    fts_indexer = FTSIndexer(test_db)
    retriever = HybridRetriever(test_db, fts_indexer)
    processor = FrameProcessor(frame_repo, obs_repo, alert_repo, event_repo)
    return {
        "db": test_db,
        "frame_repo": frame_repo,
        "obs_repo": obs_repo,
        "alert_repo": alert_repo,
        "event_repo": event_repo,
        "fts_indexer": fts_indexer,
        "retriever": retriever,
        "processor": processor
    }

@pytest.fixture
def populated_test_env(test_repos):
    processor = test_repos["processor"]
    packets = generate_simulated_packets()
    for p in packets:
        processor.process_frame(p)
    return test_repos

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
