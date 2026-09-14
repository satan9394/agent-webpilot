"""Browser launcher and process detachment manager for Chrome CDP."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Optional

import requests

logger = logging.getLogger("agent_webpilot.browser")


class ChromeLauncher:
    """Manages launching independent Chrome instances with detached process tree."""

    DEFAULT_WINDOWS_PATHS = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    DEFAULT_MAC_PATHS = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    DEFAULT_LINUX_PATHS = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]

    def __init__(
        self,
        port: int = 9222,
        user_data_dir: Optional[str] = None,
        chrome_path: Optional[str] = None,
        headless: bool = False,
    ):
        self.port = port
        self.user_data_dir = os.path.abspath(user_data_dir) if user_data_dir else self._default_profile_dir()
        self.chrome_path = chrome_path or self.find_chrome_executable()
        self.headless = headless

    @staticmethod
    def _default_profile_dir() -> str:
        cache_dir = Path.home() / ".cache" / "agent-webpilot-profile"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return str(cache_dir)

    @classmethod
    def find_chrome_executable(cls) -> Optional[str]:
        """Auto-detect installed Chrome executable across platforms."""
        # 1. Check system PATH
        which_path = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chromium")
        if which_path:
            return which_path

        # 2. Check standard OS installation directories
        system = platform.system()
        candidates: List[str] = []
        if system == "Windows":
            candidates = cls.DEFAULT_WINDOWS_PATHS
        elif system == "Darwin":
            candidates = cls.DEFAULT_MAC_PATHS
        else:
            candidates = cls.DEFAULT_LINUX_PATHS

        for path in candidates:
            if os.path.isfile(path):
                return path

        return None

    def is_port_open(self, timeout: float = 2.0) -> bool:
        """Check if CDP remote debugging port is responsive."""
        try:
            resp = requests.get(f"http://127.0.0.1:{self.port}/json/version", timeout=timeout)
            return resp.status_code == 200 and "Browser" in resp.json()
        except Exception:
            return False

    def build_launch_args(self, target_url: str = "about:blank") -> List[str]:
        """Construct isolated Chrome startup parameters."""
        args = [
            f"--remote-debugging-port={self.port}",
            "--remote-debugging-address=127.0.0.1",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--remote-allow-origins=*",
        ]
        if self.headless:
            args.append("--headless=new")
        args.append(target_url)
        return args

    def launch(self, target_url: str = "about:blank", max_wait: float = 15.0) -> bool:
        """Launch Chrome in a completely detached process tree.
        
        Ensures parent Agent process interruption will NOT kill the Chrome instance.
        """
        if self.is_port_open():
            logger.info("CDP port %d is already open and ready.", self.port)
            return True

        if not self.chrome_path:
            raise FileNotFoundError("Google Chrome or Chromium executable not found on host machine.")

        args = [self.chrome_path] + self.build_launch_args(target_url)
        logger.info("Launching detached Chrome: %s", " ".join(args))

        system = platform.system()
        if system == "Windows":
            # DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP
            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            subprocess.Popen(
                args,
                creationflags=creationflags,
                close_fds=True,
                shell=False,
            )
        else:
            # POSIX setsid detachment
            subprocess.Popen(
                args,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        # Await port readiness
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.is_port_open():
                logger.info("Chrome CDP successfully initialized on port %d.", self.port)
                return True
            time.sleep(0.5)

        raise TimeoutError(f"Chrome failed to open CDP port {self.port} within {max_wait} seconds.")
