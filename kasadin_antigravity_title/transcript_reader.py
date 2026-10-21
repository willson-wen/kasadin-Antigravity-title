"""
kasadin-Antigravity-title 对话上下文提取器
从 Antigravity 的 transcript.jsonl 及 conversation_summaries.db 中提取真实对话线索
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ConversationContext:
    conversation_id: str
    existing_title: str = ""
    preview: str = ""
    user_requests: List[str] = field(default_factory=list)
    assistant_summaries: List[str] = field(default_factory=list)
    uploaded_files: List[str] = field(default_factory=list)
    has_error: bool = False
    error_clues: List[str] = field(default_factory=list)

    @property
    def primary_request(self) -> str:
        """主要用户意图（通常来自第一条或关键一条用户需求）"""
        if self.user_requests:
            return self.user_requests[0]
        return self.preview.strip()

    @property
    def latest_request(self) -> str:
        """最近一轮的用户需求"""
        if self.user_requests:
            return self.user_requests[-1]
        return self.preview.strip()


def clean_user_content(content: str) -> str:
    """清理 Antigravity 注入的 XML 标签与元数据"""
    if not content:
        return ""

    # 提取 <USER_REQUEST> ... </USER_REQUEST>
    m = re.search(r"<USER_REQUEST>(.*?)(?:</USER_REQUEST>|$)", content, re.DOTALL)
    if m:
        text = m.group(1).strip()
    else:
        text = content

    # 移除 <ADDITIONAL_METADATA> 等标签块
    text = re.sub(r"<ADDITIONAL_METADATA>.*?(?:</ADDITIONAL_METADATA>|$)", "", text, flags=re.DOTALL)
    text = re.sub(r"<USER_SETTINGS_CHANGE>.*?(?:</USER_SETTINGS_CHANGE>|$)", "", text, flags=re.DOTALL)
    text = re.sub(r"<system_instructions>.*?(?:</system_instructions>|$)", "", text, flags=re.DOTALL)

    # 过滤多余空行
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines).strip()


def extract_context(
    brain_dir: Path,
    conversation_id: str,
    existing_title: str = "",
    preview: str = "",
    fallback_user_body: str = "",
) -> ConversationContext:
    """提取对话上下文"""
    ctx = ConversationContext(
        conversation_id=conversation_id,
        existing_title=existing_title or "",
        preview=preview or "",
    )

    transcript_path = brain_dir / conversation_id / ".system_generated" / "logs" / "transcript.jsonl"

    if transcript_path.exists():
        try:
            with transcript_path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        step = json.loads(line)
                    except Exception:
                        continue

                    stype = step.get("type")
                    content = step.get("content") or ""

                    # 提取用户请求
                    if stype == "USER_INPUT" and content:
                        cleaned = clean_user_content(content)
                        if cleaned:
                            ctx.user_requests.append(cleaned)

                    # 提取助手思考或回复
                    elif stype == "PLANNER_RESPONSE":
                        thinking = step.get("thinking") or ""
                        if thinking:
                            # 提取思考中的前两句
                            short_thought = thinking.strip().split("\n")[0][:120]
                            ctx.assistant_summaries.append(short_thought)
                            if "error" in thinking.lower() or "bug" in thinking.lower() or "fail" in thinking.lower():
                                ctx.has_error = True
                                ctx.error_clues.append(short_thought)

                    # 提取上传文件/媒体线索
                    media = step.get("media") or []
                    if isinstance(media, list):
                        for m in media:
                            uri = m.get("uri") or ""
                            if uri:
                                ctx.uploaded_files.append(Path(uri).name)
        except Exception:
            pass

    # 如果 transcript 中没有提取到用户需求，回退到 FTS 的 user_body
    if not ctx.user_requests and fallback_user_body:
        cleaned = clean_user_content(fallback_user_body)
        if cleaned:
            ctx.user_requests.append(cleaned)

    # 检查是否有错误/Bug关键词
    combined_text = (ctx.primary_request + " " + " ".join(ctx.assistant_summaries)).lower()
    if any(k in combined_text for k in ("报错", "bug", "error", "exception", "failed", "排查", "crash")):
        ctx.has_error = True

    return ctx
