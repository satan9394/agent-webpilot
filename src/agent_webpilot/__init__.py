"""Agent-WebPilot: Enterprise Agent-Native Web Automation & Anti-Detection Runtime via Chrome CDP."""

from .client import CDPClient
from .browser import ChromeLauncher
from .dom import NativeDOM
from .actions import PageActions
from .stealth import StealthEngine, StealthConfig
from .mcp_server import MCPServer

__version__ = "0.1.0"
__all__ = [
    "CDPClient",
    "ChromeLauncher",
    "NativeDOM",
    "PageActions",
    "StealthEngine",
    "StealthConfig",
    "MCPServer",
]
