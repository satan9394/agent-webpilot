"""High-level browser and page interaction actions with hybrid fallback."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

from .client import CDPClient
from .dom import NativeDOM
from .stealth import StealthEngine


class PageActions:
    """Combines CDP low-level protocols, Native DOM hijacking, and anti-detection heuristics
    into reliable user-level automated workflows.
    """

    def __init__(
        self,
        client: CDPClient,
        dom: Optional[NativeDOM] = None,
        stealth: Optional[StealthEngine] = None,
    ):
        self.client = client
        self.dom = dom or NativeDOM(client)
        self.stealth = stealth or StealthEngine()

    def navigate(
        self, url: str, wait_selector: Optional[str] = None, timeout: float = 20.0
    ) -> bool:
        """Navigates to a target URL and waits for readiness or an element."""
        self.client.send("Page.navigate", {"url": url})
        self.stealth.sleep()

        if wait_selector:
            return self.dom.wait_for_selector(wait_selector, timeout=timeout)
        return True

    def hybrid_click(
        self,
        selector: str,
        force_unhide: bool = True,
        use_cdp_first: bool = True,
        timeout: float = 5.0,
    ) -> bool:
        """Robust hybrid click combining physical coordinate dispatch and DOM fallback.
        
        Overcomes two major failure modes of naive automation:
        1. Hidden hover elements (opacity: 0 or display: none) - unhides before clicking.
        2. Dialog/modal z-index overlays blocking CDP coordinate clicks - falls back
           to native DOM dispatchEvent / .click().
        """
        # 1. Wait for element to exist
        if not self.dom.wait_for_selector(selector, timeout=timeout):
            return False

        # 2. Force unhide if requested
        if force_unhide:
            self.dom.unhide_element(selector)

        # 3. Retrieve bounding box
        box = self.dom.get_element_box(selector)

        # 4. Attempt CDP physical coordinate click
        if use_cdp_first and box and box.get("visible"):
            cx = box["center_x"]
            cy = box["center_y"]

            # Smooth human cursor simulation
            trajectory = self.stealth.generate_bezier_trajectory((0, 0), (cx, cy), steps=8)
            for x, y in trajectory[::3]:
                try:
                    self.client.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
                except Exception:
                    pass

            self.client.click_coordinate(cx, cy)
            self.stealth.sleep()
            return True

        # 5. Fallback: JavaScript native .click()
        click_js = f"""
        (function() {{
            const el = document.querySelector({json.dumps(selector)});
            if (!el) return false;
            el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
            el.click();
            return true;
        }})();
        """
        res = bool(self.client.evaluate(click_js))
        self.stealth.sleep()
        return res

    def fill_input(self, selector: str, value: Any) -> bool:
        """Injects text into a form input with React/Vue native setter support."""
        res = self.dom.set_controlled_value(selector, value)
        self.stealth.sleep()
        return bool(res and res.get("success"))

    def fill_form(self, fields: Dict[str, Any]) -> Dict[str, bool]:
        """Fills multiple form inputs in sequence with human-like intervals.
        
        Args:
            fields: Dict mapping CSS selectors to values.
            
        Returns:
            Dict mapping selectors to success booleans.
        """
        results = {}
        for sel, val in fields.items():
            ok = self.fill_input(sel, val)
            results[sel] = ok
        return results

    def get_text(self, selector: str = "body") -> Optional[str]:
        """Gets visible text content from the target selector or whole document."""
        return self.dom.query_text(selector)

    def scroll(self, direction: str = "down", amount: int = 450) -> None:
        """Smoothly scrolls the active page."""
        delta = amount if direction == "down" else -amount
        self.client.evaluate(f"window.scrollBy({{ top: {delta}, behavior: 'smooth' }});")
        self.stealth.sleep()

    def screenshot(self, output_path: str = "screenshot.png") -> str:
        """Captures page screenshot via CDP and saves to disk."""
        return self.client.capture_screenshot(output_path)
