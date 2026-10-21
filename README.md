# 🧩 kasadin-Antigravity-title

> 让你的 **Antigravity** 对话侧边栏一目了然、清晰有序。

`kasadin-Antigravity-title` 是专为 Google Antigravity 设计的会话智能规范化命名系统。基于 **「类别 emoji + 具体对象｜核心目标」** 黄金法则，提取用户核心工作意图，对 Antigravity 历史与当前会话进行结构化重命名。

---

## 🌟 一眼看清会话在做什么

| 原来混乱/默认的标题 | kasadin-Antigravity-title 规范化标题 | 类别解析 |
| :--- | :--- | :--- |
| `Antigravity 項目对话命名` | `🧩 kasadin-Antigravity-title｜对话命名系统开发与部署` | 🧩 工具开发 |
| `Seedance 2.0 创意选题与脚本规划` | `🎬 Seedance 2.0｜创作者创意选题与脚本规划` | 🎬 创意制作 |
| `AMD Radeon RX 9000 Pricing` | `🔎 AMD Radeon RX 9000｜价格与规格调研` | 🔎 对比调研 |
| `安克AI黑客松参赛感想总结` | `📝 安克AI黑客松｜参赛感想与复盘总结` | 📝 知识整理 |
| `Macro Green Sichuan Pepper` | `🎨 青花椒摄影｜8K微距静物提示词设计` | 🎨 界面视觉 |
| `Accessing Local Feishu Cli` | `⚙️ 飞书CLI｜本地访问与配置联调` | ⚙️ 环境配置 |
| `拒绝无理亲戚要求` | `💬 人际沟通｜拒绝亲戚无理要求话术` | 💬 自由探讨 |
| `<无标题> (有bug截图)` | `⚙️ MCP服务｜连接配置与报错排查` | ⚙️ 环境排错 |

---

## 📐 核心命名设计原则

1. **对象在前，目标在后**：
   - 提取产品名、库名、模块名或核心主题前置，一眼定位工作对象。
2. **恰好一个全角「｜」**：
   - 两侧严禁空格，保持视觉紧凑整齐。
3. **8 大固定业务类别**：
   - 🧩 工具开发：代码实现、Skill/插件/Agent编写、Bug修复
   - ⚙️ 环境配置：依赖安装、环境搭建、CLI排查、数据库连接
   - 🔎 对比调研：技术选型、竞品分析、模型评测、价格调查
   - 🎨 界面视觉：UI/UX 设计、CSS 排版、生图提示词设计
   - 📝 知识整理：复盘总结、文档撰写、文章草稿、面试笔记
   - 🎬 创意制作：视频选题、分镜脚本、文案策划、短视频创作
   - 📅 项目规划：任务排期、待办拆解、Roadmap规划
   - 💬 自由探讨：概念咨询、话术沟通、思想探讨
4. **长度安全与语言自洽**：
   - 中文建议 10～26 个汉字，总长严格控制在 48 字符以内。
5. **绝对安全第一**：
   - 任何写入操作前自动创建 SQLite ACID 级全量快照，支持秒级 `restore` 还原。

---

## 🚀 快速上手

本项目无需繁琐依赖，直接使用 Python 3 标准库即可运行！

```bash
# 进入项目目录
cd "kasadin-antigravity-title"

# 1. 运行环境与健康检查
python3 scripts/run.py doctor

# 2. 查看当前会话标题规范率统计
python3 scripts/run.py status

# 3. 预览所有非标会话的新标题（只读，不修改任何数据）
python3 scripts/run.py preview --unformatted-only
```

---

## 🛠️ CLI 常用命令手册

### 1. 检查与列出会话
```bash
# 检查 Antigravity 数据目录与数据库连通性
python3 scripts/run.py doctor

# 查看格式合规率与备份快照数
python3 scripts/run.py status

# 列出顶层侧边栏会话
python3 scripts/run.py list --limit 20
```

### 2. 预览与重命名单条会话
```bash
# 预览指定会话（支持前缀匹配，如 086b）
python3 scripts/run.py preview 086b

# 为指定会话自动生成规范标题并生效
python3 scripts/run.py rename 086b --apply

# 手动指定自定义规范标题
python3 scripts/run.py rename 086b --title "🧩 核心模块｜功能开发与联调" --apply
```

### 3. 一键全量批量重命名
```bash
# 对所有非标会话批量重命名（自动在前置创建时间戳快照）
python3 scripts/run.py batch --apply --unformatted-only
```

### 4. 数据库快照与安全回滚
```bash
# 手动创建当前 Antigravity 会话数据库快照
python3 scripts/run.py backup

# 从最近一次快照一键恢复数据库
python3 scripts/run.py restore
```

---

## 🧩 Antigravity 原生 Skill 集成

本项目已内置标准的 Antigravity Skill（位于 `skills/kasadin-antigravity-title/SKILL.md`），并已软链接至 `~/.gemini/antigravity/skills/kasadin-antigravity-title`。

在 Antigravity 任意对话中，你只需直接对 Agent 说：
- *“帮我用 kasadin-title 检查一下会话命名覆盖率”*
- *“预览并整理我过去的未命名会话”*
- *“把当前对话按照规范重命名”*

---

## 📂 项目结构

```text
kasadin-antigravity-title/
├── README.md                      # 项目说明文档
├── LICENSE                        # MIT 开源许可证
├── pyproject.toml                 # 包元数据
├── prompts/
│   └── naming.md                  # 核心命名规范与 Prompt
├── kasadin_antigravity_title/     # 核心功能包
│   ├── __init__.py
│   ├── config.py                  # 路径定位与配置管理
│   ├── db_adapter.py              # SQLite 读写、FTS5维护与备份恢复
│   ├── transcript_reader.py       # 轨迹与对话意图提取
│   ├── validator.py               # 规范校验与 Emoji/长度验证
│   ├── engine.py                  # 实体识别与高精度启发式引擎
│   └── cli.py                     # 命令行终端界面
├── scripts/
│   └── run.py                     # 免安装一键运行脚本
├── skills/
│   └── kasadin-antigravity-title/ # Antigravity Skill 定义
└── tests/                         # 自动化单元测试集
```

---

## 📄 License

[MIT License](LICENSE) © 2026 kasadin
