# Agent-WebPilot 🚀

<p align="center">
  <a href="README.md">English</a> | <b>简体中文</b>
</p>

[![CI](https://github.com/satan9394/agent-webpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/satan9394/agent-webpilot/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/satan9394/agent-webpilot)](https://github.com/satan9394/agent-webpilot/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Protocol: MCP](https://img.shields.io/badge/MCP-Standard%20Stdio-green.svg)](https://modelcontextprotocol.io/)

> **基于 Chrome DevTools Protocol (CDP) 的企业级 Agent 网页自动化执行与防风控运行时。**

---

## 🌟 为什么需要 Agent-WebPilot？

现代 AI 编码与自主智能体（Claude Code、Antigravity、OpenCode、AutoGPT 等）在执行真实业务场景的网页操作时，往往依赖各类“Browser Skills”。然而，传统的浏览器自动化框架（Playwright、Puppeteer、Selenium）在企业生产和强反爬站点中面临着严重的硬伤：

| 挑战维度 | 传统 Browser Skill / 无头沙箱 | Agent-WebPilot（Chrome CDP 原生直连） |
| :--- | :--- | :--- |
| **反爬风控指纹** | `navigator.webdriver = true`，缺少用户真实历史指纹，极易被 Cloudflare、极验、阿里云盾等秒级拦截。 | **0 指纹暴露**。直接通过远程调试端口（CDP）驱动宿主机真实 Google Chrome，复用真实 Canvas/WebGL 硬件指纹与 Session。 |
| **进程生命周期** | 浏览器作为 Agent 运行时的子进程挂载。Agent 发生超时、崩溃或重启时，浏览器进程树被连坐杀死，丢失全部会话。 | **操作系统级脱壳隔离**。Windows 下使用 `DETACHED_PROCESS`，POSIX 下使用独立会话，Agent 断开重启后 Chrome 实例依然存活。 |
| **SPA 受控组件失效** | Vue3 / React 的受控表单由 Virtual DOM 状态机驱动，普通 `el.value = ...` 仅修改表面 DOM，失焦保存即被重置还原。 | **原生 Setter 劫持与冒泡合成**。直接提取底层 `PropertyDescriptor.set` 注入数值，并连续派发具冒泡属性的 `input` 与 `change` 事件。 |
| **遮罩层与悬浮隐藏** | 针对仅 Hover 显示的按钮点击失败；针对被 `.dialog-layer` 遮罩层遮挡的元素直接报坐标无法穿透。 | **混合退避调度策略**。自动强制暴露（Unhide）悬浮目标；在物理坐标点击受阻时，无缝退避为 DOM 原生 `.click()` 并回读校验。 |
| **动作时序与轨迹** | 固定死板的等待时间（如 `sleep(1)`）极易被 WAF 的行为统计学模型标记为自动化脚本。 | **泊松分布随机延迟与贝塞尔轨迹**。拟合真实人类交互的泊松事件到达间隔与高斯抖动，移动鼠标时自动生成三次贝塞尔曲线。 |
| **人机验证卡死** | 遇到滑块或验证码时直接抛出异常、崩溃或陷入死循环重试。 | **人在循环（HITL）自愈守卫**。自动检测风控关键词并安全挂起，通知人工在打开的 Chrome 中完成验证后自动恢复流水线。 |

---

## 🏗️ 系统技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                   AI Agent / 智能体客户端                    │
│      (Claude Code / Antigravity / OpenCode / MCP Client)     │
└──────────────┬───────────────────────────────┬──────────────┘
               │ JSON-RPC (Stdio)              │ Python API / 命令行 CLI
               ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent-WebPilot 运行时                    │
│  ┌───────────────────────┐       ┌───────────────────────┐  │
│  │   MCPServer (Stdio)   │       │   CLI (agent-webpilot)│  │
│  └───────────┬───────────┘       └───────────┬───────────┘  │
│              └───────────────┬───────────────┘              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                PageActions & StealthEngine            │  │
│  │  - 泊松随机延迟生成器        - 三次贝塞尔鼠标拟人轨迹   │  │
│  │  - 风控特征词智能扫描        - 人在循环 (HITL) 熔断守卫 │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              NativeDOM (SPA 原生 Setter 劫持)         │  │
│  │  - Vue3 / React 原型描述符强行赋值                    │  │
│  │  - 深度冒泡合成事件广播 (input / change / blur)        │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  CDPClient (原生 WebSocket)           │  │
│  │  - JSON-RPC DevTools 协议  - 真实视口物理坐标点击     │  │
│  │  - 全局高保真截图生成        - 动态 DOM 节点树回读    │  │
│  └───────────────────────────┬───────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │ WebSocket (ws://127.0.0.1:9222)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           独立脱壳运行的本机真实 Google Chrome 实例          │
│  - 专属 User Data Profile 目录   - 进程树完全独立防闪退     │
│  - 完整保留历史 Cookie 与登录态  - 零 WebDriver 自动化标记  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 安装方法

### 1. 从源码本地安装

```bash
git clone https://github.com/satan9394/agent-webpilot.git
cd agent-webpilot
pip install -e .
```

### 2. 使用 pip 直接安装

```bash
pip install git+https://github.com/satan9394/agent-webpilot.git
```

---

## 🚀 快速上手

### 第一步：脱壳拉起带调试端口的独立 Chrome

```bash
# 启动脱壳 Chrome，使用独立配置文件目录，监听 9222 调试端口
agent-webpilot launch --port 9222 --user-data-dir ./chrome_profile
```

### 第二步：Python API 自动化交互

```python
from agent_webpilot import CDPClient, ChromeLauncher, NativeDOM, PageActions, StealthEngine

# 1. 建立 CDP 客户端连接
client = CDPClient(port=9222)
client.connect()

dom = NativeDOM(client)
stealth = StealthEngine()
actions = PageActions(client, dom, stealth)

try:
    # 2. 打开目标页面，等待关键选择器就位
    actions.navigate("https://example.com/login", wait_selector="#username")

    # 3. 穿透 Vue3 / React 受控组件注入表单数据
    actions.fill_input("#username", "alice_dev")
    actions.fill_input("#password", "example_secret_token")

    # 4. 执行混合点击（坐标点击 + 遮罩层穿透退避 + 悬浮显示）
    actions.hybrid_click("button[type='submit']")

    # 5. 读取文本内容或捕获屏幕快照
    dashboard_text = actions.get_text(".dashboard-greeting")
    actions.screenshot("dashboard.png")
finally:
    client.close()
```

---

## 🤖 MCP (Model Context Protocol) 协议集成

Agent-WebPilot 内置标准 Stdio MCP 服务，支持无缝接入各类现代 AI Coding Agent（如 Claude Desktop、Claude Code、Antigravity 等）。

### 在 `claude_desktop_config.json` 中配置：

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

### 提供的 MCP 工具清单：
- `webpilot_launch_browser`: 脱壳拉起带远程调试端口的 Chrome 浏览器。
- `webpilot_navigate`: 控制页面导航跳转，支持选择器就位等待。
- `webpilot_click`: 智能混合点击（支持自动 unhide 与遮罩穿透）。
- `webpilot_fill_input`: 表单输入注入（穿透 Vue/React 受控属性锁定）。
- `webpilot_get_text`: 提取指定选择器或页面的纯文本内容。
- `webpilot_screenshot`: 捕获当前浏览器视口的屏幕快照。
- `webpilot_eval_js`: 在页面运行时上下文中安全执行任意 JavaScript 表达式。

---

## 💻 命令行 CLI 使用手册

```bash
# 1. 脱壳启动 Chrome
agent-webpilot launch --port 9222

# 2. 页面导航
agent-webpilot navigate https://news.ycombinator.com

# 3. 提取网页文本
agent-webpilot text ".titleline > a"

# 4. 表单注入
agent-webpilot fill "input[name='q']" "Agentic AI"

# 5. 执行智能点击
agent-webpilot click "button.search-submit"

# 6. 保存视口快照
agent-webpilot screenshot search_result.png
```

---

## 🛡️ 防风控与隐匿算法深度解析

### 1. 泊松拟人交互延迟生成器
固定周期的 `sleep` 是爬虫与自动化脚本被风控系统识别的最常见特征。Agent-WebPilot 将操作间隔建模为泊松到达过程：
$$\Delta t = -\ln(U) \cdot \lambda + \mathcal{N}(0, \sigma^2)$$
配合用户可配置的上下界（默认 0.35s ~ 1.65s），真实复刻人类打字与浏览时的节奏起伏。

### 2. 三次贝塞尔鼠标移动轨迹
在下发物理坐标点击前，自动构建起止点之间的三次贝塞尔曲线，并在控制点引入随机偏角与高斯位移，模拟人体手臂神经传导与鼠标微动。

### 3. 人在循环（HITL）自愈机制
自动扫描页面中的风险特征（如 `"验证码"`、`"captcha"`、`"安全验证"`、`"异常访问"`）。一旦命中风控拦截，流程不会直接崩溃退出，而是安全挂起并输出提示，等待操作人员在打开的 Chrome 中点击完成验证后自动恢复继续执行。

---

## 🧪 自动化测试

运行全量单元测试套件：

```bash
pytest tests/ -v
```

---

## 👥 贡献者（Contributors）

欢迎所有开源社区同仁的参与与建议！详细规范请查阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

- **核心作者与维护者**：[@satan9394](https://github.com/satan9394)
- 衷心感谢所有为该项目提出建议、反馈 Bug 和提交 PR 的开发者。

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。
