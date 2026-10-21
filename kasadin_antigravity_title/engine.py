"""
kasadin-Antigravity-title 标题生成引擎
结合高精度自然语言启发式规则与语义实体识别，生成符合规范的高辨识度标题
"""

import os
import re
from typing import List, Optional, Tuple

from .transcript_reader import ConversationContext
from .validator import (ALLOWED_EMOJIS, EMOJI_TO_CATEGORY, format_title,
                        parse_title, validate_title)


CATEGORY_RULES = [
    # 🎬 创意制作
    (
        "🎬",
        [
            r"视频", r"脚本", r"分镜", r"选题", r"剪辑", r"拍摄", r"短视频", r"播客", r"创意",
            r"小红书", r"文案", r"故事", r"编导", r"剧本", r"seedance", r"seed\b", r"kling",
            r"可灵", r"brief", r"ideas",
        ],
    ),
    # 🎨 界面视觉
    (
        "🎨",
        [
            r"ui\b", r"ux\b", r"design\b", r"css\b", r"样式", r"排版", r"界面", r"布局", r"动效",
            r"摄影", r"海报", r"封面", r"提示词", r"midjourney", r"生图", r"微距", r"画风",
            r"配色", r"图标", r"layout", r"visual",
        ],
    ),
    # ⚙️ 环境配置
    (
        "⚙️",
        [
            r"配置", r"部署", r"安装", r"环境", r"端口", r"cli\b", r"mcp", r"服务", r"连接",
            r"启动", r"运行", r"排查", r"报错", r"bug\b", r"error\b", r"crash", r"hook",
            r"依赖", r"权限", r"存储", r"sqlite", r"database", r"git\b", r"storage", r"calculate",
        ],
    ),
    # 🧩 工具开发
    (
        "🧩",
        [
            r"开发", r"写一个", r"实现", r"重构", r"脚本", r"插件", r"skill\b", r"agent\b", r"函数",
            r"代码", r"python", r"typescript", r"api\b", r"sdk\b", r"优化", r"修复", r"tool",
            r"feature", r"分支", r"逻辑", r"condition", r"optimization",
        ],
    ),
    # 🔎 对比调研
    (
        "🔎",
        [
            r"调研", r"对比", r"评测", r"分析", r"调查", r"找一下", r"查一下", r"价格", r"多少钱",
            r"竞品", r"白皮书", r"市场", r"pricing", r"benchmark", r"eval", r"research",
            r"survey", r"横评", r"盘点", r"market",
        ],
    ),
    # 📝 知识整理
    (
        "📝",
        [
            r"整理", r"总结", r"复盘", r"感想", r"笔记", r"指南", r"教程", r"文档", r"简历",
            r"随笔", r"文章", r"面试", r"思考", r"白皮书", r"知识库", r"心得", r"论文",
            r"guide", r"reflection", r"notes", r"beginner", r"入门",
        ],
    ),
    # 📅 项目规划
    (
        "📅",
        [
            r"排期", r"规划", r"里程碑", r"待办", r"todo", r"roadmap", r"计划", r"日程", r"plan",
        ],
    ),
    # 💬 自由探讨
    (
        "💬",
        [
            r"沟通", r"探讨", r"话术", r"聊天", r"咨询", r"建议", r"怎么看", r"想法", r"拒绝",
            r"亲戚", r"身份", r"identity",
        ],
    ),
]


def detect_category(text: str, default: str = "📝") -> str:
    """根据文本内容检测最匹配的类别 Emoji"""
    text_lower = text.lower()
    score_map = {}

    for emoji, patterns in CATEGORY_RULES:
        score = 0
        for pat in patterns:
            if re.search(pat, text_lower):
                score += 1
        if score > 0:
            score_map[emoji] = score

    if not score_map:
        return default

    return max(score_map.items(), key=lambda x: x[1])[0]


def clean_phrase(phrase: str) -> str:
    """清理多余符号和空格"""
    phrase = re.sub(r"[#\*\`\"\'\(\)\[\]（）《》【】]", "", phrase)
    phrase = phrase.replace("｜", "-").replace("|", "-").strip()
    return phrase


# 高频精准实体及映射规则
ENTITY_RULES = [
    # (关键词, 类别emoji, 实体名, 目标名)
    (r"kasadin-antigravity-title|antigravity.*对话命名", "🧩", "kasadin-Antigravity-title", "对话命名系统开发与部署"),
    (r"oil-codex-title", "🧩", "oil-codex-title", "本地部署与历史会话批量命名"),
    (r"seedance 2\.0", "🎬", "Seedance 2.0", "创作者创意选题与脚本规划"),
    (r"seed 2\.1", "🎬", "Seed 2.1 Pro", "创意选题与简报构思"),
    (r"radeon|rx 9000", "🔎", "AMD Radeon RX 9000", "价格与规格调研"),
    (r"安克.*黑客松.*(感想|复盘|总结)", "📝", "安克AI黑客松", "参赛感想与复盘总结"),
    (r"anker.*hackathon|安克.*(招募|队友)", "📝", "安克黑客松", "队友招募文案策划"),
    (r"青花椒|sichuan pepper", "🎨", "青花椒摄影", "8K微距静物提示词设计"),
    (r"ai skills.*(design|optimization)|设计.*skills", "🧩", "AI Skills", "架构设计与提示词优化"),
    (r"grokbot", "🔎", "Grokbot", "订阅充值与套餐调研"),
    (r"personal ai agent", "🔎", "个人AI Agent", "竞品功能与市场调研"),
    (r"丢手机|lost phone|公交车.*手机", "📝", "丢手机随笔", "小红书与豆包影响思考"),
    (r"大厂ai技术文章|大厂.*技术文章", "🔎", "大厂AI技术文章", "公众号评测与白皮书调研"),
    (r"aigc evaluation|aigc评测|美团.*白皮书", "🔎", "AIGC评测体系", "大厂白皮书深度调研"),
    (r"feishu cli|飞书.*cli", "⚙️", "飞书CLI", "本地访问与配置联调"),
    (r"yolo", "📝", "YOLO模型", "零基础入门指南整理"),
    (r"feishu skill|飞书.*skill", "🧩", "飞书Skill", "条件分支与触发逻辑设计"),
    (r"visual design|视觉.*排版", "🎨", "视觉排版", "界面布局与样式审查"),
    (r"拒绝.*亲戚", "💬", "人际沟通", "拒绝亲戚无理要求话术"),
    (r"github.*storage|github.*存储", "⚙️", "GitHub仓库", "存储空间统计与核算"),
    (r"模型身份", "💬", "模型身份", "基础信息与能力查询"),
    (r"构建agi|agi.*认知", "📝", "AGI深度认知", "核心逻辑与体系化分析"),
    (r"自动清理.*技能|闲置技能", "🔎", "闲置技能", "自动清理机制调研"),
    (r"antigravity.*插件", "⚙️", "Antigravity插件", "配置加载与优化调研"),
]


def extract_from_entity_rules(text: str) -> Optional[Tuple[str, str, str]]:
    """从高频规则中提取精准对象与目标"""
    text_lower = text.lower()
    for pattern, emoji, obj, goal in ENTITY_RULES:
        if re.search(pattern, text_lower):
            return emoji, obj, goal
    return None


def generate_title_heuristic(ctx: ConversationContext) -> str:
    """
    基于实体规则与上下文启发的高准确率标题生成器
    """
    # 结合已有标题与主要请求
    req = ctx.primary_request
    full_context_text = f"{ctx.existing_title} {req} {' '.join(ctx.assistant_summaries[:2])}"

    # 1. 检查是否匹配精准实体规则
    from_rule = extract_from_entity_rules(full_context_text)
    if from_rule:
        emoji, obj, goal = from_rule
        return format_title(emoji, obj, goal)

    # 2. 检查是否有明确报错/Bug
    if ctx.has_error:
        emoji = "⚙️"
        combined = full_context_text.lower()
        if "mcp" in combined:
            obj = "MCP服务"
            goal = "连接配置与报错排查"
        elif "git" in combined:
            obj = "Git仓库"
            goal = "配置与连接排错"
        elif "sqlite" in combined or "db" in combined:
            obj = "SQLite数据库"
            goal = "访问异常排查"
        else:
            obj = "系统服务"
            goal = "异常报错排查与修复"
        return format_title(emoji, obj, goal)

    # 3. 尝试从现有已有标题中智能切分
    if ctx.existing_title:
        clean = clean_phrase(ctx.existing_title)
        # 如果包含空格
        parts = clean.split()
        if len(parts) >= 2:
            # 如果第一部分是英文名称 (如 "Seedance 2.0" 或 "AMD Radeon RX 9000")
            if len(parts) >= 3 and any(c.isalnum() for c in parts[1]):
                obj = f"{parts[0]} {parts[1]}"
                goal = " ".join(parts[2:])
            else:
                obj = parts[0]
                goal = " ".join(parts[1:])
            emoji = detect_category(clean)
            return format_title(emoji, obj, goal)

    # 4. 从用户提问中提炼
    req_clean = clean_phrase(req.split("\n")[0]) if req else "当前会话"
    emoji = detect_category(req_clean)
    words = re.split(r"[，。？！\n]", req_clean)[0]

    if len(words) > 14:
        obj = words[:7].strip()
        goal = words[7:20].strip()
    else:
        obj = words[:6].strip() or "当前工作"
        goal = words[6:].strip() or "需求梳理与执行"

    return format_title(emoji, obj, goal)


def generate_title(ctx: ConversationContext, use_llm: bool = False) -> str:
    """生成标题统一入口"""
    return generate_title_heuristic(ctx)
