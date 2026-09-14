# Contributing to Agent-WebPilot / 贡献指南

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

Thank you for your interest in contributing to **Agent-WebPilot**! We welcome contributions, bug reports, feature requests, and pull requests from developers across the globe.

### How Can You Contribute?
1. **Reporting Bugs**: If you encounter an issue or platform incompatibility, please open a GitHub Issue with clear steps to reproduce and system details.
2. **Feature Suggestions**: Have ideas for better anti-detection heuristics, new CDP bindings, or MCP extensions? Open a Feature Request issue.
3. **Submitting Pull Requests**:
   - Fork the repository and create your feature branch: `git checkout -b feat/your-feature-name`.
   - Ensure all existing and new tests pass: `pytest tests/`.
   - Maintain code quality and typing standards (Python 3.10+ compatible).
   - Write clear, semantic commit messages (e.g. `feat: add support for iframe selector resolution`).
   - Push your branch and open a Pull Request against `main`.

### Code of Conduct
- Be respectful, constructive, and collaborative.
- Ensure no sensitive information, credentials, or proprietary tokens are committed.

---

<a name="中文"></a>
## 中文

感谢您对 **Agent-WebPilot** 项目的关注与支持！我们热烈欢迎来自社区的任何贡献，包括 Issue 反馈、功能建议与代码提交（PR）。

### 参与贡献的方式
1. **提交 Bug 反馈**：若在特定操作系统或网页遇到自动化失败或反爬兼容问题，请创建 Issue 并详细附上复现步骤、操作系统及 Chrome 版本。
2. **提出新特性建议**：如果您对新版 CDP 特性、新型拟人轨迹、框架受控表单注入有更好点子，欢迎提出 Feature 讨论。
3. **提交代码合并（Pull Request）**：
   - Fork 本仓库并在本地创建分支：`git checkout -b feat/新功能名称`。
   - 运行并确保全量测试通过：`pytest tests/`。
   - 遵循 Python 3.10+ 代码风格与类型注解规约。
   - 编写清晰的 Git 提交信息（如 `fix: 修复特定遮罩层下点击坐标偏移的问题`）。
   - 推送分支并提交针对 `main` 分支的 Pull Request。

### 行为准则
- 保持友善、包容与建设性的交流氛围。
- 绝不在代码或提交记录中包含任何私有凭证、密钥或未脱敏数据。
