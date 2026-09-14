"""Chrome DevTools Protocol (CDP) WebSocket JSON-RPC Client."""

from __future__ import annotations

import base64
import json
import logging
import random
import time
from typing import Any, Dict, List, Optional

import requests
import websocket

logger = logging.getLogger("agent_webpilot.client")


class CDPError(Exception):
    """Base exception for CDP protocol errors."""
    pass


class CDPConnectionError(CDPError):
    """Raised when unable to connect to CDP endpoint."""
    pass


class CDPClient:
    """High-performance direct Chrome DevTools Protocol Client over WebSocket."""

    def __init__(self, cdp_url: str = "http://127.0.0.1:9222", timeout: float = 30.0):
        self.cdp_url = cdp_url.rstrip("/")
        self.timeout = timeout
        self._ws: Optional[websocket.WebSocket] = None
        self._target_id: Optional[str] = None
        self._ws_url: Optional[str] = None

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and self._ws.connected

    def get_version(self) -> Dict[str, Any]:
        """Fetch browser version and protocol metadata."""
        try:
            resp = requests.get(f"{self.cdp_url}/json/version", timeout=4)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise CDPConnectionError(f"Failed to connect to CDP version endpoint at {self.cdp_url}: {e}") from e

    def list_targets(self) -> List[Dict[str, Any]]:
        """List all active inspectable browser targets/tabs."""
        try:
            resp = requests.get(f"{self.cdp_url}/json", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise CDPConnectionError(f"Failed to list targets from {self.cdp_url}: {e}") from e

    def find_target(self, url_pattern: str = "", target_type: str = "page") -> Optional[Dict[str, Any]]:
        """Locate a matching target tab by URL substring or pattern."""
        targets = self.list_targets()
        for t in targets:
            if target_type and t.get("type") != target_type:
                continue
            if not url_pattern or url_pattern in t.get("url", ""):
                return t
        return None

    def connect(self, target_url_pattern: str = "", target_id: Optional[str] = None) -> None:
        """Establish WebSocket connection to the designated target page."""
        if target_id:
            targets = self.list_targets()
            target = next((t for t in targets if t.get("id") == target_id), None)
        else:
            target = self.find_target(target_url_pattern)

        if not target:
            raise CDPConnectionError(f"No inspectable target matching '{target_url_pattern or target_id}' found.")

        ws_url = target.get("webSocketDebuggerUrl")
        if not ws_url:
            raise CDPConnectionError(f"Target {target.get('id')} has no webSocketDebuggerUrl attached.")

        self._target_id = target.get("id")
        self._ws_url = ws_url

        try:
            self._ws = websocket.create_connection(ws_url, timeout=self.timeout)
            self._ws.settimeout(self.timeout)
            logger.info("Connected to CDP target %s via %s", self._target_id, self._ws_url)
        except Exception as e:
            raise CDPConnectionError(f"WebSocket handshake failed with {ws_url}: {e}") from e

    def close(self) -> None:
        """Close current WebSocket connection gracefully."""
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
            finally:
                self._ws = None

    def send_command(self, method: str, params: Optional[Dict[str, Any]] = None, mid: Optional[int] = None) -> Dict[str, Any]:
        """Send JSON-RPC command and await synchronous response with ID matching."""
        if not self.is_connected:
            raise CDPConnectionError("CDPClient is not connected. Call connect() first.")

        req_id = mid or random.randint(10000, 999999)
        payload = {"id": req_id, "method": method, "params": params or {}}
        self._ws.send(json.dumps(payload))

        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"Timed out waiting for response to command {method} (id={req_id})")

            raw_msg = self._ws.recv()
            msg = json.loads(raw_msg)
            if msg.get("id") == req_id:
                if "error" in msg:
                    raise CDPError(f"CDP command '{method}' failed: {msg['error']}")
                return msg.get("result", {})

    def evaluate(self, expression: str, await_promise: bool = True, return_by_value: bool = True) -> Any:
        """Execute JavaScript expression via Runtime.evaluate and return result value."""
        params = {
            "expression": expression,
            "awaitPromise": await_promise,
            "returnByValue": return_by_value,
        }
        res = self.send_command("Runtime.evaluate", params)
        result_obj = res.get("result", {})
        if res.get("exceptionDetails"):
            raise CDPError(f"JavaScript evaluation exception: {res['exceptionDetails']}")
        return result_obj.get("value")

    def click_coordinate(self, x: float, y: float, button: str = "left", click_count: int = 1) -> None:
        """Dispatch real physical mouse click events (mousePressed + mouseReleased)."""
        self.send_command("Input.dispatchMouseEvent", {
            "type": "mousePressed",
            "x": x,
            "y": y,
            "button": button,
            "clickCount": click_count,
        })
        self.send_command("Input.dispatchMouseEvent", {
            "type": "mouseReleased",
            "x": x,
            "y": y,
            "button": button,
            "clickCount": click_count,
        })

    def capture_screenshot(self, format: str = "png", quality: Optional[int] = None) -> bytes:
        """Capture viewport screenshot as raw image bytes."""
        params: Dict[str, Any] = {"format": format}
        if quality is not None:
            params["quality"] = quality
        res = self.send_command("Page.captureScreenshot", params)
        return base64.b64decode(res["data"])

    def get_document_title(self) -> str:
        """Convenience method to read document.title."""
        return str(self.evaluate("document.title") or "")

    def get_inner_text(self, selector: str = "body") -> str:
        """Read innerText of a specified DOM element."""
        expr = f"document.querySelector({json.dumps(selector)})?.innerText || ''"
        return str(self.evaluate(expr) or "")
