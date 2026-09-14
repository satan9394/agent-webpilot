"""Tests for ChromeLauncher configuration and arguments."""

import os
from agent_webpilot.browser import ChromeLauncher


def test_launcher_default_args():
    launcher = ChromeLauncher(port=9333, user_data_dir="./test_profile", headless=True)
    assert launcher.port == 9333
    assert launcher.headless is True
    assert launcher.user_data_dir == os.path.abspath("./test_profile")


def test_find_chrome_returns_string_or_none():
    launcher = ChromeLauncher()
    path = launcher.find_chrome_executable()
    # On most developer systems with Chrome, this should find chrome.exe or return None if absent
    if path:
        assert isinstance(path, str)
        assert os.path.exists(path)
