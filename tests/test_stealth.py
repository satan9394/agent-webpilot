"""Tests for StealthEngine and anti-detection algorithms."""

import pytest
from agent_webpilot.stealth import StealthConfig, StealthEngine


def test_stealth_delay_bounds():
    config = StealthConfig(min_delay=0.2, max_delay=1.0, poisson_lambda=0.5)
    engine = StealthEngine(config)
    for _ in range(50):
        delay = engine.calculate_human_delay()
        assert 0.2 <= delay <= 1.0


def test_risk_detection():
    engine = StealthEngine()
    
    clean_text = "欢迎登录系统，请点击提交您的求职申请。"
    assert engine.detect_risk_trigger(clean_text) is None

    captcha_text = "检测到异常访问，请完成下方滑块验证以继续。"
    matched = engine.detect_risk_trigger(captcha_text)
    assert matched is not None
    assert "滑块" in matched or "异常" in matched


def test_bezier_trajectory():
    engine = StealthEngine()
    start = (100, 200)
    end = (500, 600)
    path = engine.generate_bezier_trajectory(start, end, steps=10)
    
    assert len(path) == 11
    assert path[0] == (100, 200)
    assert path[-1] == (500, 600)
    for pt in path:
        assert isinstance(pt[0], int)
        assert isinstance(pt[1], int)
