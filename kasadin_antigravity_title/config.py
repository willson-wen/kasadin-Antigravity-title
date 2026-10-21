"""
kasadin-Antigravity-title 路径与环境配置
"""

import os
from pathlib import Path

DEFAULT_ANTIGRAVITY_DIR = Path(os.path.expanduser("~/.gemini/antigravity"))


class Config:
    def __init__(self, antigravity_dir: Path = None):
        target = antigravity_dir or os.environ.get("ANTIGRAVITY_DATA_DIR") or DEFAULT_ANTIGRAVITY_DIR
        self.antigravity_dir = Path(target)
        self.db_path = self.antigravity_dir / "conversation_summaries.db"
        self.brain_dir = self.antigravity_dir / "brain"
        self.annotations_dir = self.antigravity_dir / "annotations"
        self.backup_dir = self.antigravity_dir / "backups" / "kasadin-title"
        self.skills_dir = self.antigravity_dir / "skills"

    def ensure_dirs(self):
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def is_antigravity_installed(self) -> bool:
        return self.antigravity_dir.exists() and self.db_path.exists()
