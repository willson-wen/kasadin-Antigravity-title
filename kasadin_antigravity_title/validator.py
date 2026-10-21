"""
kasadin-Antigravity-title 标题格式校验器
遵循规范：{类别 emoji} {具体对象}｜{核心目标}
"""

import re
from typing import Optional, Tuple

ALLOWED_EMOJIS = ("🎬", "🧩", "🔎", "📝", "📅", "🎨", "⚙️", "💬")

EMOJI_TO_CATEGORY = {
    "🎬": "创意制作",
    "🧩": "工具开发",
    "🔎": "对比调研",
    "📝": "知识整理",
    "📅": "项目规划",
    "🎨": "界面视觉",
    "⚙️": "环境配置",
    "⚙": "环境配置",
    "💬": "自由探讨",
}

CATEGORY_TO_EMOJI = {
    "创意制作": "🎬",
    "工具开发": "🧩",
    "对比调研": "🔎",
    "知识整理": "📝",
    "项目规划": "📅",
    "界面视觉": "🎨",
    "环境配置": "⚙️",
    "自由探讨": "💬",
}

# 使用显式交集匹配包含变体选择符的 Emoji (如 U+2699 U+FE0F)
TITLE_PATTERN = re.compile(
    r"^(🎬|🧩|🔎|📝|📅|🎨|⚙️|⚙|💬)\s+([^｜\s][^｜]*?)｜([^｜\s][^｜]*?)$"
)


def validate_title(title: str) -> Tuple[bool, str]:
    """
    校验标题是否完全符合规范：
    - 长度在 4 到 48 个字符之间
    - 必须以允许的类别 emoji 开头，且后接一个半角空格
    - 恰好一个全角「｜」作为对象与目标的分隔符
    - 对象与目标均不为空，且不以空格包围
    - 不含换行符等控制字符
    """
    if not isinstance(title, str):
        return False, "标题必须为字符串"

    title = title.strip()
    if not title:
        return False, "标题不能为空"

    if len(title) > 48:
        return False, f"标题长度超过 48 个字符（当前 {len(title)} 字符）"

    if "\n" in title or "\r" in title:
        return False, "标题不能包含换行符"

    if "|" in title:
        return False, "检测到半角 '|'，必须使用全角 '｜'"

    if title.count("｜") != 1:
        return False, f"必须且仅能包含一个全角 '｜'（当前出现 {title.count('｜')} 次）"

    m = TITLE_PATTERN.match(title)
    if not m:
        if not any(title.startswith(e) for e in ("🎬", "🧩", "🔎", "📝", "📅", "🎨", "⚙️", "⚙", "💬")):
            return False, f"标题缺少允许的类别 emoji（支持：{' '.join(ALLOWED_EMOJIS)}）"
        if not re.match(r"^(🎬|🧩|🔎|📝|📅|🎨|⚙️|⚙|💬)\s+", title):
            return False, "类别 emoji 后必须且只能跟一个半角空格"
        return False, "标题不符合「{emoji} {对象}｜{目标}」结构"

    emoji, obj, goal = m.group(1), m.group(2).strip(), m.group(3).strip()

    if not obj:
        return False, "对象部分不能为空"
    if not goal:
        return False, "核心目标部分不能为空"

    return True, "符合规范"


def parse_title(title: str) -> Optional[Tuple[str, str, str, str]]:
    """
    解析标题组件：(emoji, 类别名称, 具体对象, 核心目标)
    如果不符合格式则返回 None
    """
    is_valid, _ = validate_title(title)
    if not is_valid:
        return None

    m = TITLE_PATTERN.match(title.strip())
    if not m:
        return None

    raw_emoji = m.group(1)
    # 统一规范化为 ⚙️
    emoji = "⚙️" if raw_emoji in ("⚙", "⚙️") else raw_emoji
    category = EMOJI_TO_CATEGORY.get(emoji, "未知")
    obj = m.group(2).strip()
    goal = m.group(3).strip()
    return emoji, category, obj, goal


def format_title(emoji: str, obj: str, goal: str) -> str:
    """
    根据组件合成标准标题
    """
    emoji = emoji.strip()
    if emoji == "⚙":
        emoji = "⚙️"
    if emoji not in ALLOWED_EMOJIS:
        raise ValueError(f"不支持的 Emoji: {emoji}，必须为: {ALLOWED_EMOJIS}")

    obj = obj.strip().replace("｜", "-").replace("|", "-")
    goal = goal.strip().replace("｜", "-").replace("|", "-")

    candidate = f"{emoji} {obj}｜{goal}"
    if len(candidate) > 48:
        overflow = len(candidate) - 48
        goal = goal[:-overflow].rstrip()
        candidate = f"{emoji} {obj}｜{goal}"

    return candidate
