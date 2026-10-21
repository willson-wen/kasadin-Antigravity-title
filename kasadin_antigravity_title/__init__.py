"""
kasadin-Antigravity-title: 让你的 Antigravity 会话列表清晰一目了然
"""

__version__ = "0.1.0"
__author__ = "kasadin"

from .config import Config
from .db_adapter import DBAdapter
from .engine import generate_title
from .transcript_reader import extract_context
from .validator import format_title, parse_title, validate_title

__all__ = [
    "Config",
    "DBAdapter",
    "extract_context",
    "format_title",
    "generate_title",
    "parse_title",
    "validate_title",
]
