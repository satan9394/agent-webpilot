# Release v0.1.0: Enterprise Agent-Native Web Automation via Chrome CDP / 企业级 Agent 网页自动化与防风控底座

[English](#english) | [中文说明](#chinese)

---

<a name="english"></a>
## 🚀 English Release Notes

**Agent-WebPilot v0.1.0** marks the initial official release of the enterprise agent-native web automation and anti-detection runtime. Engineered specifically for modern AI Coding Agents (Claude Code, Antigravity, OpenCode, AutoGPT), this release overcomes the fundamental limitations of traditional Browser Skills (Playwright, Puppeteer, Selenium) when operating in real-world production and anti-bot protected platforms.

### ✨ Key Features & Highlights

1. **Native Chrome CDP Communication**:
   - Zero-dependency, lightweight JSON-RPC WebSocket client directly communicating with Chrome DevTools Protocol.
   - Eliminates webdriver flags (`navigator.webdriver = false`), automated window borders, and runtime inspection hooks.

2. **Decoupled Detached Process Architecture**:
   - OS-level process tree detachment (`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` on Windows, POSIX new session).
   - Chrome instances run independently with dedicated User Data Profiles, surviving Agent restarts, crashes, and re-connections without session or cookie loss.

3. **Reactive SPA Native Setter Hijacking**:
   - Directly overrides `HTMLInputElement.prototype` property descriptors to bypass Vue3 and React Virtual DOM event masking.
   - Dispatches bubbling synthetic `input`, `change`, and `blur` events, guaranteeing 100% form value retention.

4. **Hybrid Coordinate & DOM Fallback Click**:
   - Automatically unhides hidden hover elements via CSS property override and scrolling.
   - Seamlessly falls back from physical CDP viewport coordinate clicks to native DOM `.click()` when blocked by `.dialog-layer` backdrop masks.

5. **Poisson Human Latency & Cubic Bezier Trajectories**:
   - Replaces naive fixed `sleep()` delays with Poisson arrival intervals ($\Delta t = -\ln(U) \cdot \lambda + \mathcal{N}(0, \sigma^2)$).
   - Generates authentic neuromuscular cursor movement curves with randomized control point deviation.

6. **Human-In-The-Loop (HITL) Guard**:
   - Automatically scans page DOM for anti-bot hurdles and CAPTCHA keywords (`"验证码"`, `"captcha"`, `"security check"`).
   - Gracefully pauses execution and alerts operator to resolve the hurdle in the open browser window before auto-resuming.

7. **Standard Stdio Model Context Protocol (MCP) Server**:
   - Built-in MCP server exposing 7 automation tools (`webpilot_launch_browser`, `webpilot_navigate`, `webpilot_click`, `webpilot_fill_input`, `webpilot_get_text`, `webpilot_screenshot`, `webpilot_eval_js`).
   - Plug-and-play with Claude Desktop, Claude Code, and Antigravity.

8. **CLI Tooling**:
   - Easy-to-use standalone CLI: `agent-webpilot launch | navigate | click | fill | text | screenshot | eval | mcp`.

### 📦 Installation

```bash
# Direct from PyPI distribution wheel (attached below)
pip install agent_webpilot-0.1.0-py3-none-any.whl

# Or directly from GitHub
pip install git+https://github.com/satan9394/agent-webpilot.git
```

---

<a name="chinese"></a>
## 🇨🇳 中文发布说明

**Agent-WebPilot v0.1.0** 正式发布！这是专为现代 AI 编码与自主智能体（Claude Code、Antigravity、OpenCode、DeepSeek Harness 等）量身打造的企业级网页自动化与防风控运行时，彻底攻克了传统 Browser Skill 在复杂 Web 与强风控平台上的反爬封禁、SPA 表单赋值丢失以及 Agent 中断连坐杀进程等业界痛点。

### 🌟 核心特性与技术攻关

1. **原生 Chrome CDP 直连协议**：
   - 基于原生 WebSocket JSON-RPC 与 Chrome DevTools Protocol 通信，摆脱臃肿的 WebDriver 依赖。
   - 绝不注入自动化特征指纹（`navigator.webdriver = false`），完全复用本机真实浏览器硬件指纹与 Session。

2. **操作系统级脱壳隔离架构**：
   - Windows 下采用 `DETACHED_PROCESS`，POSIX 下采用独立会话脱壳，彻底实现浏览器生命周期与 Agent 运行时的物理隔离。
   - 支持独立 User Data Profile 隔离存储，Agent 发生中断、超时或重启时，浏览器实例永不闪退，Cookie 与登录态长期持久化。

3. **Vue3 / React 受控组件深层穿透（Native Setter 劫持）**：
   - 提取底层原型链 `PropertyDescriptor.set` 强行注入数值，并连续分发具冒泡属性的合成 `input` 与 `change` 事件。
   - 彻底解决现代 SPA 框架下普通 JS 赋值被 Virtual DOM 状态机重置清空的行业顽疾。

4. **混合退避点击调度**：
   - 针对悬浮显形的隐形按钮，提供先居中并强制覆盖 `style.display='block'` 后再派发真实物理坐标点击的调度机制。
   - 针对 `.dialog-layer` 遮罩层遮挡，自适应退避为 DOM 原生 `.click()` 并配合状态机回读纠偏，保证长链流程 100% 确定性。

5. **泊松拟人交互延迟与三次贝塞尔轨迹**：
   - 抛弃固定 `sleep()`，采用符合人类动作到达规律的泊松分布随机延迟模型与高斯微抖动。
   - 移动鼠标坐标时自动拟合三次贝塞尔曲线，完美模拟手臂神经传导与微动。

6. **人在循环（HITL）自愈守卫**：
   - 智能识别风控关键词（如“验证码”、“滑块”、“异常访问”），遇到验证时安全挂起，等待人工在 Chrome 中完成验证后自动恢复，绝不崩溃或陷入死循环。

7. **内置标准 Stdio MCP 服务**：
   - 提供 7 大浏览器操控工具，无需二次开发即可直接挂载进 Claude Code、Claude Desktop 或 Antigravity。

8. **全功能 CLI 工具集**：
   - 提供 `agent-webpilot launch | navigate | click | fill | text | screenshot | eval | mcp` 命令行工具。

### 📦 安装与下载

```bash
# 通过本 Release 附带的 Wheel 包直接安装
pip install agent_webpilot-0.1.0-py3-none-any.whl

# 或直接通过 GitHub 仓库安装
pip install git+https://github.com/satan9394/agent-webpilot.git
```
