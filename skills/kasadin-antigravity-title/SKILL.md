---
name: kasadin-antigravity-title
description: Antigravity 会话智能规范化命名系统。检查环境状态、预览会话标题、为当前或指定会话命名、批量重命名历史会话，以及提供数据库安全快照与恢复。当用户提到会话命名、侧边栏整理、整理历史对话或使用 kasadin-antigravity-title 时调用。
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

## 入口脚本与常用命令

脚本入口位于本项目根目录下的 `scripts/run.py`。

### 1. 环境诊断与状态
```bash
python3 scripts/run.py doctor
python3 scripts/run.py status
```

### 2. 查看会话列表与合规情况
```bash
python3 scripts/run.py list
```

### 3. 预览会话标题
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

### 6. 安全快照与一键恢复
```bash
# 创建手动快照
python3 scripts/run.py backup

# 从最近一次快照一键恢复
python3 scripts/run.py restore
```
