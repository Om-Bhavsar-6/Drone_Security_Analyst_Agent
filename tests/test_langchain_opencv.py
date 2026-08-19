import pytest
import os
from pathlib import Path
from app.pipeline.cv_utils import DroneCVRenderer
from app.agent.langchain_agent import LangChainSecurityToolkit
from app.pipeline.simulator import generate_simulated_packets
from app.ai.mock_vlm import MockVLMEngine

def test_opencv_frame_rendering(tmp_path):
    renderer = DroneCVRenderer(output_dir=tmp_path)
    vlm = MockVLMEngine()
    packets = generate_simulated_packets()
    
    p1 = packets[0]
    obs1 = vlm.analyze_frame(p1)
    
    saved_path = renderer.generate_and_annotate_frame(p1, obs1)
    if saved_path:
        assert os.path.exists(saved_path)
        assert saved_path.endswith(".jpg")

def test_langchain_toolkit_tools(populated_test_env):
    toolkit = LangChainSecurityToolkit(
        retriever=populated_test_env["retriever"],
        frame_repo=populated_test_env["frame_repo"],
        alert_repo=populated_test_env["alert_repo"],
        event_repo=populated_test_env["event_repo"]
    )
    tools = toolkit.get_tools()
    assert len(tools) == 4
    tool_names = [t.name for t in tools]
    assert "search_surveillance_frames" in tool_names
    assert "get_security_alerts" in tool_names
    assert "get_cross_frame_events" in tool_names
    assert "get_mission_shift_summary" in tool_names
