---
name: kasadin-antigravity-title
description: Antigravity 会话智能规范化命名系统。检查环境状态、首次安装主动引导整理、预览会话标题、为当前或指定会话命名、批量重命名历史会话，以及提供数据库安全快照与恢复。当用户提到会话命名、侧边栏整理、整理历史对话或使用 kasadin-antigravity-title 时调用。
metadata:
  compatibility: Antigravity 原生扩展；支持 macOS、Linux 与 Windows；需要 Python 3.8+。
---

# kasadin-Antigravity-title

为 Antigravity 会话提供基于「类别 emoji + 具体对象｜核心目标」标准的高辨识度智能命名与历史整理。

## 核心命名规范

统一结构：`{类别 emoji} {具体对象}｜{核心目标}`

- **8 大标准类别**：
  - 🧩 工具开发（代码编写、插件、MCP、Agent、Bug修复）
  - ⚙️ 环境配置（依赖安装、本地部署、服务搭建、排错）
  - 🔎 对比调研（竞品分析、技术选型、模型评测、价格调研）
  - 🎨 界面视觉（UI/UX设计、前端还原、生图提示词设计）
  - 📝 知识整理（文档、面试复盘、学习笔记、随笔总结）
  - 🎬 创意制作（视频选题、分镜脚本、短视频策划、文案构思）
  - 📅 项目规划（里程碑排期、任务待办、Roadmap）
  - 💬 自由探讨（概念咨询、人际沟通、头脑风暴）
- **对象在前**：具体模块、产品名或核心实体。
- **全角分隔**：恰好一个全角「｜」，两侧不留空格。
- **长度限制**：中文建议 10～26 字，总长度不超过 48 字符。

---

## 🤖 Agent 行为指南与首次安装引导

当你（Agent）感知到用户安装了本 Skill、首次提及本 Skill，或询问关于侧边栏/会话标题整理时，严格遵循以下流程：

### 1. 首次接入主动检测
在响应用户前，先在后台运行状态检查：
```bash
python3 scripts/run.py status
```
根据返回的统计数据（`unformatted` 和 `empty` 数量）：

- **如果存在非标或空白会话（数量 > 0）**：
  主动向用户发起引导询问：
  > “检测到你当前 Antigravity 侧边栏中有 **{top_level}** 个历史会话（其中 **{unformatted + empty}** 个尚未采用结构化规范命名，当前规范覆盖率为 **{compliance}%**）。
  > 
  > **需不需要我帮你扫描并批量格式化整理你 Antigravity 过去所有的历史对话？**
  > 
  > 💡 *整理前会自动为数据库创建时间戳安全快照，随时支持一键完整还原。*”

- **如果已 100% 规范化**：
  向用户反馈当前规范率已达 100%，并告知后续有新对话随时可以唤起整理。

### 2. 用户确认后的执行分支
- **用户要求“先看看/预览”**：
  执行 `python3 scripts/run.py preview --unformatted-only`，以 Markdown 表格或清晰列表展示前后对比，等待用户确认写入。
- **用户要求“直接整理/一键改掉/执行”**：
  执行 `python3 scripts/run.py batch --apply --unformatted-only`，完成后汇报处理结果与快照备份名称。
- **用户要求“只改当前对话”**：
  获取当前对话 ID，执行 `python3 scripts/run.py rename <CONVERSATION_ID> --apply`。

---

## 脚本入口与 CLI 命令参考

脚本入口位于本项目根目录下的 `scripts/run.py`。

### 1. 环境诊断与状态统计
```bash
python3 scripts/run.py doctor
python3 scripts/run.py status
```

### 2. 查看会话列表与合规情况
```bash
python3 scripts/run.py list --limit 30
```

### 3. 预览会话标题（只读安全）
```bash
# 预览所有非标会话的新标题
python3 scripts/run.py preview --unformatted-only

# 预览指定会话（支持前缀匹配）
python3 scripts/run.py preview <CONVERSATION_ID>
```

### 4. 单条会话重命名并生效
```bash
# 自动生成并立即写入
python3 scripts/run.py rename <CONVERSATION_ID> --apply

# 手动指定新标题并写入
python3 scripts/run.py rename <CONVERSATION_ID> --title "🧩 核心模块｜重命名测试" --apply
```

### 5. 批量重命名历史会话
```bash
# 批量执行（自动创建时间戳安全备份）
python3 scripts/run.py batch --apply --unformatted-only
```

### 6. 安全快照与一键回滚
```bash
# 创建手动快照
python3 scripts/run.py backup

# 从最近一次快照一键恢复
python3 scripts/run.py restore
```
