"""Anti-Detection Engine, Poisson Random Delay & Human-In-The-Loop Guards."""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple


@dataclass
class StealthConfig:
    """Configuration for anti-bot evasion and realistic human action timing."""
    min_delay: float = 0.35
    max_delay: float = 1.65
    poisson_lambda: float = 0.75
    enable_jitter: bool = True
    risk_keywords: List[str] = field(
        default_factory=lambda: [
            "验证码",
            "安全验证",
            "请完成下方验证",
            "滑块验证",
            "人机验证",
            "访问过于频繁",
            "异常访问",
            "captcha",
            "geetest",
            "cloudflare",
            "verify you are human",
            "security check",
        ]
    )
    hitl_auto_pause: bool = True


class StealthEngine:
    """Provides human-like behavioral emulation and anti-crawling detection."""

    def __init__(self, config: Optional[StealthConfig] = None):
        self.config = config or StealthConfig()

    def calculate_human_delay(self) -> float:
        """Calculates a delay using Poisson distribution plus Gaussian jitter.
        
        Real user browsing actions follow Poisson processes (intervals between events),
        unlike naive fixed delays (e.g. `time.sleep(1)`) easily flagged by WAF algorithms.
        """
        # Poisson generation: -ln(U) * lambda
        u = max(random.random(), 1e-6)
        interval = -math.log(u) * self.config.poisson_lambda

        if self.config.enable_jitter:
            jitter = random.gauss(0, 0.12)
            interval += jitter

        # Clamp between bounds
        interval = max(self.config.min_delay, min(interval, self.config.max_delay))
        return round(interval, 3)

    def sleep(self) -> float:
        """Applies a human-like delay and returns duration."""
        duration = self.calculate_human_delay()
        time.sleep(duration)
        return duration

    def detect_risk_trigger(self, page_content: str) -> Optional[str]:
        """Scans page content for anti-bot challenge signatures.
        
        Args:
            page_content: Text or HTML from the current page.
            
        Returns:
            The matched risk keyword, or None if clean.
        """
        lower_content = page_content.lower()
        for kw in self.config.risk_keywords:
            if kw.lower() in lower_content:
                return kw
        return None

    def request_hitl(
        self,
        reason: str,
        resume_check: Optional[Callable[[], bool]] = None,
        poll_interval: float = 2.0,
        max_wait: float = 300.0,
    ) -> bool:
        """Enters Human-In-The-Loop (HITL) mode when triggered by an anti-bot hurdle.
        
        Instead of crashing or spamming requests, execution pauses safely,
        alerting the operator to solve CAPTCHA in the native Chrome window.
        
        Args:
            reason: Description of the detected challenge.
            resume_check: Optional function returning True once cleared.
            poll_interval: Seconds between verification checks.
            max_wait: Maximum seconds to wait before timeout.
            
        Returns:
            True if resolved, False on timeout.
        """
        print(f"\n[HITL GUARD] Anti-bot challenge detected: '{reason}'")
        print("[HITL GUARD] Execution paused. Please resolve the verification in the Chrome browser.")
        print("[HITL GUARD] Waiting for resolution...\n")

        start = time.time()
        if resume_check:
            while time.time() - start < max_wait:
                time.sleep(poll_interval)
                if resume_check():
                    print("[HITL GUARD] Verification cleared! Resuming automation.\n")
                    return True
            print("[HITL GUARD] Timeout waiting for human verification resolution.")
            return False
        else:
            # Fallback to interactive console confirmation if no callback given
            try:
                input("[HITL GUARD] Press ENTER once you have cleared the verification in Chrome: ")
                return True
            except EOFError:
                return False

    @staticmethod
    def generate_bezier_trajectory(
        start: Tuple[float, float],
        end: Tuple[float, float],
        steps: int = 15,
    ) -> List[Tuple[int, int]]:
        """Generates a cubic Bezier curve simulating natural hand-guided cursor movement."""
        x0, y0 = start
        x3, y3 = end

        # Control points with random deviation
        dx = x3 - x0
        dy = y3 - y0
        cx1 = x0 + dx * random.uniform(0.1, 0.4) + random.uniform(-30, 30)
        cy1 = y0 + dy * random.uniform(0.1, 0.4) + random.uniform(-30, 30)
        cx2 = x0 + dx * random.uniform(0.6, 0.9) + random.uniform(-30, 30)
        cy2 = y0 + dy * random.uniform(0.6, 0.9) + random.uniform(-30, 30)

        path = []
        for i in range(steps + 1):
            t = i / steps
            # Cubic Bezier formula: B(t) = (1-t)^3 P0 + 3(1-t)^2 t P1 + 3(1-t) t^2 P2 + t^3 P3
            x = (
                (1 - t) ** 3 * x0
                + 3 * (1 - t) ** 2 * t * cx1
                + 3 * (1 - t) * t ** 2 * cx2
                + t ** 3 * x3
            )
            y = (
                (1 - t) ** 3 * y0
                + 3 * (1 - t) ** 2 * t * cy1
                + 3 * (1 - t) * t ** 2 * cy2
                + t ** 3 * y3
            )
            path.append((int(round(x)), int(round(y))))
        return path
