"""Standard Stdio Model Context Protocol (MCP) Server for Agent-WebPilot."""

from __future__ import annotations

import json
import sys
import traceback
from typing import Any, Dict, List, Optional

from .actions import PageActions
from .browser import ChromeLauncher
from .client import CDPClient
from .dom import NativeDOM
from .stealth import StealthEngine


class MCPServer:
    """Stdio-based Model Context Protocol server exposing browser automation capabilities."""

    def __init__(self, port: int = 9222):
        self.port = port
        self.client: Optional[CDPClient] = None
        self.dom: Optional[NativeDOM] = None
        self.actions: Optional[PageActions] = None
        self.stealth = StealthEngine()

    def _ensure_connected(self) -> PageActions:
        if not self.client or not self.client.ws or not self.client.ws.connected:
            self.client = CDPClient(port=self.port)
            self.client.connect()
            self.dom = NativeDOM(self.client)
            self.actions = PageActions(self.client, self.dom, self.stealth)
        return self.actions

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "webpilot_launch_browser",
                "description": "Launch a decoupled Google Chrome instance with remote debugging port enabled.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "port": {"type": "integer", "default": 9222, "description": "Debugging port"},
                        "user_data_dir": {"type": "string", "description": "Path to persistent profile dir"},
                        "headless": {"type": "boolean", "default": False, "description": "Run headless"},
                    },
                },
            },
            {
                "name": "webpilot_navigate",
                "description": "Navigate active Chrome tab to a URL.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target webpage URL"},
                        "wait_selector": {"type": "string", "description": "CSS selector to wait for"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "webpilot_click",
                "description": "Perform hybrid CDP/DOM click on an element (supports unhiding and overlay bypass).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector to click"},
                        "force_unhide": {"type": "boolean", "default": True, "description": "Force unhide hover elements"},
                    },
                    "required": ["selector"],
                },
            },
            {
                "name": "webpilot_fill_input",
                "description": "Fill input or textarea bypassing React/Vue synthetic state locks via native property setters.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector for input/textarea"},
                        "value": {"type": "string", "description": "Text value to inject"},
                    },
                    "required": ["selector", "value"],
                },
            },
            {
                "name": "webpilot_get_text",
                "description": "Get visible text content from the active page or element.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "default": "body", "description": "Target CSS selector"},
                    },
                },
            },
            {
                "name": "webpilot_screenshot",
                "description": "Capture a screenshot of the active browser viewport.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "output_path": {"type": "string", "default": "screenshot.png", "description": "Save path"},
                    },
                },
            },
            {
                "name": "webpilot_eval_js",
                "description": "Evaluate arbitrary JavaScript in the active page context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "JavaScript expression to evaluate"},
                    },
                    "required": ["expression"],
                },
            },
        ]

    def call_tool(self, name: str, args: Dict[str, Any]) -> Any:
        if name == "webpilot_launch_browser":
            port = args.get("port", self.port)
            user_data = args.get("user_data_dir")
            headless = args.get("headless", False)
            launcher = ChromeLauncher(port=port, user_data_dir=user_data, headless=headless)
            chrome_path = launcher.find_chrome_executable()
            if not chrome_path:
                return {"error": "Google Chrome executable not found on host system."}
            pid = launcher.launch()
            return {"success": True, "pid": pid, "port": port}

        actions = self._ensure_connected()

        if name == "webpilot_navigate":
            url = args["url"]
            wait_sel = args.get("wait_selector")
            ok = actions.navigate(url, wait_selector=wait_sel)
            return {"success": ok, "url": url}

        elif name == "webpilot_click":
            selector = args["selector"]
            force = args.get("force_unhide", True)
            ok = actions.hybrid_click(selector, force_unhide=force)
            return {"success": ok, "selector": selector}

        elif name == "webpilot_fill_input":
            selector = args["selector"]
            val = args["value"]
            ok = actions.fill_input(selector, val)
            return {"success": ok, "selector": selector}

        elif name == "webpilot_get_text":
            selector = args.get("selector", "body")
            txt = actions.get_text(selector)
            return {"text": txt}

        elif name == "webpilot_screenshot":
            path = args.get("output_path", "screenshot.png")
            saved = actions.screenshot(path)
            return {"saved_to": saved}

        elif name == "webpilot_eval_js":
            expr = args["expression"]
            res = actions.client.evaluate(expr)
            return {"result": res}

        else:
            raise ValueError(f"Unknown tool: {name}")

    def run_stdio(self) -> None:
        """Runs the JSON-RPC standard I/O loop for MCP integration."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                req = json.loads(line)
            except Exception:
                continue

            msg_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "agent-webpilot", "version": "0.1.0"},
                    },
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                pass

            elif method == "ping":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": self.list_tools()},
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                try:
                    result = self.call_tool(tool_name, tool_args)
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}
                            ]
                        },
                    }
                except Exception as e:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {"code": -32603, "message": str(e), "data": traceback.format_exc()},
                    }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
