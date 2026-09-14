"""Native DOM Manipulation & Reactive Framework Native Setter Hijack for Agent-WebPilot."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Union

from .client import CDPClient


class NativeDOM:
    """Provides DOM manipulation tailored for modern SPA frameworks (Vue3, React, Angular).
    
    Standard `element.value = '...'` does not trigger framework state bindings
    because Virtual DOM relies on native property setters and bubbling event dispatchers.
    NativeDOM hijacks prototype property descriptors and simulates authentic user input events.
    """

    def __init__(self, client: CDPClient):
        self.client = client

    def set_controlled_value(
        self, selector: str, value: Union[str, int, float]
    ) -> Dict[str, Any]:
        """Injects a value into a controlled input/textarea bypassing Virtual DOM overrides.
        
        Args:
            selector: CSS selector for the input element.
            value: The string or numeric value to set.
            
        Returns:
            Dict containing success status and actual updated value.
        """
        val_str = str(value)
        js_code = f"""
        (function() {{
            const el = document.querySelector({json.dumps(selector)});
            if (!el) {{
                return {{ success: false, error: 'Element not found: ' + {json.dumps(selector)} }};
            }}

            el.focus();

            // Locate prototype descriptor that defines 'value'
            let proto = Object.getPrototypeOf(el);
            while (proto && !Object.prototype.hasOwnProperty.call(proto, 'value')) {{
                proto = Object.getPrototypeOf(proto);
            }}
            const descriptor = proto ? Object.getOwnPropertyDescriptor(proto, 'value') : null;

            if (descriptor && descriptor.set) {{
                descriptor.set.call(el, {json.dumps(val_str)});
            }} else {{
                el.value = {json.dumps(val_str)};
            }}

            // Dispatch synthetic events matching real user typing
            el.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
            el.dispatchEvent(new Event('blur', {{ bubbles: true, cancelable: true }}));

            return {{
                success: true,
                selector: {json.dumps(selector)},
                actualValue: el.value
            }};
        }})();
        """
        return self.client.evaluate(js_code)

    def get_element_box(self, selector: str) -> Optional[Dict[str, float]]:
        """Retrieves element viewport coordinates and dimensions.
        
        Args:
            selector: CSS selector.
            
        Returns:
            Dict with x, y, width, height, center_x, center_y or None if missing.
        """
        js_code = f"""
        (function() {{
            const el = document.querySelector({json.dumps(selector)});
            if (!el) return null;
            const rect = el.getBoundingClientRect();
            return {{
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                center_x: rect.x + rect.width / 2,
                center_y: rect.y + rect.height / 2,
                visible: rect.width > 0 && rect.height > 0
            }};
        }})();
        """
        res = self.client.evaluate(js_code)
        if isinstance(res, dict) and "center_x" in res:
            return res
        return None

    def query_text(self, selector: str) -> Optional[str]:
        """Gets visible innerText of an element."""
        js_code = f"""
        (function() {{
            const el = document.querySelector({json.dumps(selector)});
            return el ? el.innerText || el.textContent : null;
        }})();
        """
        return self.client.evaluate(js_code)

    def query_elements(self, selector: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """Queries multiple elements with metadata (tag, class, text, id)."""
        js_code = f"""
        (function() {{
            const nodes = Array.from(document.querySelectorAll({json.dumps(selector)})).slice(0, {max_items});
            return nodes.map(n => {{
                const r = n.getBoundingClientRect();
                return {{
                    tag: n.tagName.toLowerCase(),
                    id: n.id || '',
                    className: n.className || '',
                    text: (n.innerText || n.textContent || '').trim().slice(0, 100),
                    rect: {{ x: r.x, y: r.y, width: r.width, height: r.height }}
                }};
            }});
        }})();
        """
        res = self.client.evaluate(js_code)
        return res if isinstance(res, list) else []

    def wait_for_selector(
        self, selector: str, timeout: float = 10.0, poll_interval: float = 0.3
    ) -> bool:
        """Polls until an element appears in the DOM or timeout occurs."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            check = self.client.evaluate(
                f"Boolean(document.querySelector({json.dumps(selector)}))"
            )
            if check is True:
                return True
            time.sleep(poll_interval)
        return False

    def unhide_element(self, selector: str) -> bool:
        """Forces an element to be visible by overriding style visibility attributes."""
        js_code = f"""
        (function() {{
            const el = document.querySelector({json.dumps(selector)});
            if (!el) return false;
            el.style.display = 'block';
            el.style.visibility = 'visible';
            el.style.opacity = '1';
            el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
            return true;
        }})();
        """
        return bool(self.client.evaluate(js_code))
