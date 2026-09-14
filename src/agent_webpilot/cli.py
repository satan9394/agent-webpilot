"""Command-line interface for Agent-WebPilot."""

from __future__ import annotations

import argparse
import json
import sys

from .actions import PageActions
from .browser import ChromeLauncher
from .client import CDPClient
from .dom import NativeDOM
from .mcp_server import MCPServer
from .stealth import StealthEngine


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="agent-webpilot",
        description="Enterprise Agent-Native Web Automation & Anti-Detection Runtime via Chrome CDP.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # launch
    p_launch = subparsers.add_parser("launch", help="Launch detached Chrome browser with debugging port")
    p_launch.add_argument("--port", type=int, default=9222, help="CDP debugging port (default: 9222)")
    p_launch.add_argument("--user-data-dir", type=str, default=None, help="User profile directory")
    p_launch.add_argument("--headless", action="store_true", help="Run in headless mode")

    # navigate
    p_nav = subparsers.add_parser("navigate", help="Navigate to URL")
    p_nav.add_argument("url", help="Target URL")
    p_nav.add_argument("--port", type=int, default=9222, help="CDP debugging port")
    p_nav.add_argument("--wait", type=str, default=None, help="Selector to wait for")

    # click
    p_click = subparsers.add_parser("click", help="Hybrid click on element")
    p_click.add_argument("selector", help="CSS selector")
    p_click.add_argument("--port", type=int, default=9222, help="CDP debugging port")

    # fill
    p_fill = subparsers.add_parser("fill", help="Fill input with Vue/React native setter bypass")
    p_fill.add_argument("selector", help="CSS selector")
    p_fill.add_argument("value", help="Value to set")
    p_fill.add_argument("--port", type=int, default=9222, help="CDP debugging port")

    # text
    p_text = subparsers.add_parser("text", help="Extract text content")
    p_text.add_argument("selector", nargs="?", default="body", help="CSS selector")
    p_text.add_argument("--port", type=int, default=9222, help="CDP debugging port")

    # screenshot
    p_shot = subparsers.add_parser("screenshot", help="Capture page screenshot")
    p_shot.add_argument("output", nargs="?", default="screenshot.png", help="Output PNG path")
    p_shot.add_argument("--port", type=int, default=9222, help="CDP debugging port")

    # eval
    p_eval = subparsers.add_parser("eval", help="Evaluate JavaScript expression")
    p_eval.add_argument("expression", help="JavaScript code snippet")
    p_eval.add_argument("--port", type=int, default=9222, help="CDP debugging port")

    # mcp
    p_mcp = subparsers.add_parser("mcp", help="Run as Model Context Protocol (MCP) server over stdio")
    p_mcp.add_argument("--port", type=int, default=9222, help="CDP debugging port")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "launch":
        launcher = ChromeLauncher(port=args.port, user_data_dir=args.user_data_dir, headless=args.headless)
        chrome_exe = launcher.find_chrome_executable()
        if not chrome_exe:
            print("[ERROR] Could not find Google Chrome on system path.", file=sys.stderr)
            sys.exit(1)
        print(f"[*] Launching Chrome: {chrome_exe}")
        pid = launcher.launch()
        print(f"[+] Detached Chrome process launched with PID {pid} on port {args.port}.")
        return

    if args.command == "mcp":
        server = MCPServer(port=args.port)
        server.run_stdio()
        return

    # For page actions, connect to CDP
    client = CDPClient(port=args.port)
    try:
        client.connect()
    except Exception as e:
        print(f"[ERROR] Failed to connect to Chrome on port {args.port}: {e}", file=sys.stderr)
        print("Tip: Run 'agent-webpilot launch' first or start Chrome with --remote-debugging-port.", file=sys.stderr)
        sys.exit(1)

    dom = NativeDOM(client)
    stealth = StealthEngine()
    actions = PageActions(client, dom, stealth)

    try:
        if args.command == "navigate":
            ok = actions.navigate(args.url, wait_selector=args.wait)
            print(f"[+] Navigated to {args.url} (Success: {ok})")

        elif args.command == "click":
            ok = actions.hybrid_click(args.selector)
            print(f"[+] Clicked '{args.selector}' (Success: {ok})")

        elif args.command == "fill":
            ok = actions.fill_input(args.selector, args.value)
            print(f"[+] Filled '{args.selector}' with '{args.value}' (Success: {ok})")

        elif args.command == "text":
            txt = actions.get_text(args.selector)
            print(txt or "")

        elif args.command == "screenshot":
            saved = actions.screenshot(args.output)
            print(f"[+] Screenshot saved to {saved}")

        elif args.command == "eval":
            res = client.evaluate(args.expression)
            print(json.dumps(res, ensure_ascii=False, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
