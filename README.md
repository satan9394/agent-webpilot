# Agent-WebPilot 🚀

[![CI](https://github.com/satan9394/agent-webpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/satan9394/agent-webpilot/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Protocol: MCP](https://img.shields.io/badge/MCP-Standard%20Stdio-green.svg)](https://modelcontextprotocol.io/)

> **Enterprise Agent-Native Web Automation & Anti-Detection Runtime via Chrome DevTools Protocol (CDP).**

---

## 🌟 Why Agent-WebPilot?

Modern AI Agents (Claude Code, Antigravity, OpenCode, AutoGPT, etc.) increasingly rely on "Browser Skills" to interact with the web. However, standard browser automation frameworks (Selenium, Puppeteer, Playwright) face severe bottlenecks in real-world production and high-security enterprise environments:

| Challenge | Traditional Browser Skills | Agent-WebPilot (Chrome CDP) |
| :--- | :--- | :--- |
| **Anti-Bot Fingerprint** | `navigator.webdriver = true`, automated window flags easily caught by Cloudflare, GeeTest, Akamai | **Zero fingerprint**. Connects to native Google Chrome via standard CDP (remote debugging port). Identical to genuine human browsing. |
| **Process Lifecycle** | Coupled to Agent runtime. If the Agent restarts or times out, the browser process terminates, losing session & cookies. | **Decoupled Detached Process**. Chrome runs as an independent OS process tree. Survives Agent restarts, crashes, and re-connections. |
| **SPA Controlled Inputs** | `element.value = '...'` does not trigger Vue3/React state machines; input reverts on blur. | **Native Setter Hijack**. Direct prototype descriptor invocation + bubbling `input`/`change` event synthesis. |
| **Dynamic Overlays & Menus** | Naive clicks fail on hover-only menus or get intercepted by dialog/modal backdrop masks. | **Hybrid Fallback Engine**. Automatically unhides hover targets; falls back between physical CDP coordinate dispatch and native DOM `.click()`. |
| **Timing & Trajectory** | Deterministic fixed intervals (`sleep(1)`) trigger behavioral WAF heuristics. | **Poisson Randomization & Bezier Paths**. Poisson event intervals + Gaussian jitter + cubic Bezier mouse curves. |
| **CAPTCHA / Challenges** | Hard crash or infinite retry loop upon encountering verification hurdles. | **Human-In-The-Loop (HITL)**. Intelligently detects verification hurdles and pauses safely for human resolution. |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   AI Agent / LLM Client                     │
│      (Claude Code / Antigravity / OpenCode / MCP Client)     │
└──────────────┬───────────────────────────────┬──────────────┘
               │ JSON-RPC (Stdio / HTTP)       │ Python API / CLI
               ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent-WebPilot Runtime                   │
│  ┌───────────────────────┐       ┌───────────────────────┐  │
│  │   MCPServer (Stdio)   │       │   CLI (agent-webpilot)│  │
│  └───────────┬───────────┘       └───────────┬───────────┘  │
│              └───────────────┬───────────────┘              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                PageActions & StealthEngine            │  │
│  │  - Poisson Delay Generator   - Cubic Bezier Mouse     │  │
│  │  - Anti-Bot Signature Guard  - HITL Fallback Flow     │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              NativeDOM (SPA Setter Hijack)            │  │
│  │  - Vue3 / React Prototype Descriptor Override         │  │
│  │  - Bubbling Synthetic Event Dispatch (input/change)   │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  CDPClient (WebSocket)                │  │
│  │  - Raw DevTools Protocol   - Physical Mouse Click     │  │
│  │  - Full Viewport Screenshot - DOM Tree Query          │  │
│  └───────────────────────────┬───────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │ WebSocket (ws://127.0.0.1:9222)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           Detached Native Google Chrome Instance            │
│  - Independent User Data Dir     - Survives Agent Crash     │
│  - Fully Preserved Cookies       - Zero Anti-Bot Footprint  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

```bash
# Clone and install locally
git clone https://github.com/satan9394/agent-webpilot.git
cd agent-webpilot
pip install -e .

# Or install directly with pip
pip install git+https://github.com/satan9394/agent-webpilot.git
```

---

## 🚀 Quick Start

### 1. Launch Independent Detached Chrome

```bash
# Launch Chrome with remote debugging on port 9222 and dedicated profile
agent-webpilot launch --port 9222 --user-data-dir ./chrome_profile
```

### 2. Python API

```python
from agent_webpilot import CDPClient, ChromeLauncher, NativeDOM, PageActions, StealthEngine

# 1. Connect to Chrome CDP
client = CDPClient(port=9222)
client.connect()

dom = NativeDOM(client)
stealth = StealthEngine()
actions = PageActions(client, dom, stealth)

try:
    # 2. Navigate with selector readiness wait
    actions.navigate("https://example.com/login", wait_selector="#username")

    # 3. Inject form values bypassing Vue3 / React Virtual DOM synthetic masking
    actions.fill_input("#username", "alice_dev")
    actions.fill_input("#password", "example_secret_token")

    # 4. Perform hybrid click (CDP coordinates + DOM fallback + hover unhide)
    actions.hybrid_click("button[type='submit']")

    # 5. Extract text or capture viewport snapshot
    page_text = actions.get_text(".dashboard-greeting")
    actions.screenshot("dashboard.png")
finally:
    client.close()
```

---

## 🤖 MCP (Model Context Protocol) Integration

Agent-WebPilot provides a built-in MCP server over Stdio for seamless integration with AI coding assistants:

### Claude Desktop / Claude Code (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agent-webpilot": {
      "command": "python",
      "args": ["-m", "agent_webpilot.cli", "mcp", "--port", "9222"]
    }
  }
}
```

### Supported MCP Tools:
- `webpilot_launch_browser`: Launch detached Chrome with remote debugging.
- `webpilot_navigate`: Open URL with readiness wait.
- `webpilot_click`: Hybrid coordinate / DOM click with auto-unhide.
- `webpilot_fill_input`: React / Vue native setter form injection.
- `webpilot_get_text`: Query visible text from selector.
- `webpilot_screenshot`: Capture viewport screenshot.
- `webpilot_eval_js`: Execute arbitrary JavaScript expressions.

---

## 💻 CLI Commands

```bash
# Launch Chrome
agent-webpilot launch --port 9222

# Navigate to page
agent-webpilot navigate https://news.ycombinator.com

# Extract text content
agent-webpilot text ".titleline > a"

# Fill inputs
agent-webpilot fill "input[name='q']" "Agentic AI"

# Hybrid click
agent-webpilot click "button.search-submit"

# Capture screenshot
agent-webpilot screenshot search_result.png
```

---

## 🛡️ Anti-Detection & Stealth Design

### 1. Poisson Human Latency Simulation
Fixed intervals (`sleep(1.0)`) are the #1 telltale sign of web scraping bots. Agent-WebPilot models interaction delays as a Poisson arrival process:
$$\Delta t = -\ln(U) \cdot \lambda + \mathcal{N}(0, \sigma^2)$$
clamped within user-configurable bounds (default $0.35s - 1.65s$).

### 2. Cubic Bezier Cursor Trajectories
Before executing coordinate clicks, cursor movements are simulated along smooth cubic Bezier curves with randomized lateral deviation, matching authentic neuromuscular behavior.

### 3. Human-In-The-Loop (HITL) Auto-Detection
When risk keywords (`"验证码"`, `"captcha"`, `"security check"`, `"异常访问"`) are detected, the system safely pauses execution, logs an alert, and prompts the operator to resolve the challenge directly in the open Chrome window before resuming automatically.

---

## 🧪 Testing

Run the automated test suite:

```bash
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
