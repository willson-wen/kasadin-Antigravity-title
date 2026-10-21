#!/usr/bin/env python3
"""
kasadin-Antigravity-title 快捷执行入口
"""

import sys
from pathlib import Path

# 将项目根目录加入模块搜索路径
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kasadin_antigravity_title.cli import main

if __name__ == "__main__":
    main()
