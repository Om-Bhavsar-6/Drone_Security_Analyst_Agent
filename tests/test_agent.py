import pytest
from app.models.query import ChatRequest
from app.agent.tools import SecurityAgentTools
from app.agent.assistant import SecurityAnalystAssistant

def test_agent_answers_vehicle_tracking(populated_test_env):
    tools = SecurityAgentTools(
        retriever=populated_test_env["retriever"],
        frame_repo=populated_test_env["frame_repo"],
        alert_repo=populated_test_env["alert_repo"],
        event_repo=populated_test_env["event_repo"]
    )
    agent = SecurityAnalystAssistant(tools)
    
    resp = agent.process_query(ChatRequest(prompt="How many times was the blue Ford truck observed today?"))
    assert resp.intent == "vehicle_tracking"
    assert "Ford F150" in resp.response or "truck" in resp.response.lower()
    assert "2 time(s)" in resp.response or "2" in resp.response
    assert len(resp.tools_used) >= 1

def test_agent_answers_night_loitering(populated_test_env):
    tools = SecurityAgentTools(
        retriever=populated_test_env["retriever"],
        frame_repo=populated_test_env["frame_repo"],
        alert_repo=populated_test_env["alert_repo"],
        event_repo=populated_test_env["event_repo"]
    )
    agent = SecurityAnalystAssistant(tools)
    
    resp = agent.process_query(ChatRequest(prompt="Was anyone loitering near the main gate at night?"))
    assert resp.intent == "security_threat_inquiry"
    assert "alert" in resp.response.lower() or "suspicious" in resp.response.lower()
