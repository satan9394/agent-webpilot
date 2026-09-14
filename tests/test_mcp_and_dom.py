"""Tests for MCP server schema and NativeDOM logic with mocked client."""

from unittest.mock import MagicMock
from agent_webpilot.mcp_server import MCPServer
from agent_webpilot.dom import NativeDOM


def test_mcp_server_tools_list():
    server = MCPServer(port=9222)
    tools = server.list_tools()
    tool_names = [t["name"] for t in tools]
    
    assert "webpilot_launch_browser" in tool_names
    assert "webpilot_navigate" in tool_names
    assert "webpilot_click" in tool_names
    assert "webpilot_fill_input" in tool_names
    assert "webpilot_get_text" in tool_names
    assert "webpilot_screenshot" in tool_names
    assert "webpilot_eval_js" in tool_names
    
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool


def test_native_dom_set_controlled_value():
    mock_client = MagicMock()
    mock_client.evaluate.return_value = {"success": True, "selector": "#name", "actualValue": "demo_user"}
    
    dom = NativeDOM(mock_client)
    res = dom.set_controlled_value("#name", "demo_user")
    
    assert res["success"] is True
    assert res["actualValue"] == "demo_user"
    assert mock_client.evaluate.called
    eval_call_arg = mock_client.evaluate.call_args[0][0]
    assert "getOwnPropertyDescriptor" in eval_call_arg
    assert "dispatchEvent" in eval_call_arg


def test_native_dom_get_box():
    mock_client = MagicMock()
    mock_client.evaluate.return_value = {
        "x": 100.0, "y": 200.0, "width": 80.0, "height": 30.0,
        "center_x": 140.0, "center_y": 215.0, "visible": True
    }
    
    dom = NativeDOM(mock_client)
    box = dom.get_element_box("#submit-btn")
    assert box is not None
    assert box["center_x"] == 140.0
    assert box["visible"] is True
