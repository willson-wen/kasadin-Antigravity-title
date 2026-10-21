"""
kasadin-Antigravity-title 单元测试: 对话上下文提取器
"""

import json
import tempfile
import unittest
from pathlib import Path

from kasadin_antigravity_title.transcript_reader import clean_user_content, extract_context


class TestTranscriptReader(unittest.TestCase):
    def test_clean_user_content(self):
        raw = """<USER_REQUEST>
帮我写一个 Python 脚本
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-10-21T23:00:00+08:00
</ADDITIONAL_METADATA>"""
        cleaned = clean_user_content(raw)
        self.assertEqual(cleaned, "帮我写一个 Python 脚本")

    def test_extract_context_from_transcript(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            brain_dir = Path(tmpdir)
            conv_id = "test-conv-123"
            logs_dir = brain_dir / conv_id / ".system_generated" / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            transcript_file = logs_dir / "transcript.jsonl"

            steps = [
                {
                    "step_index": 0,
                    "type": "USER_INPUT",
                    "content": "<USER_REQUEST>\n设计一个 Antigravity 插件\n</USER_REQUEST>",
                },
                {
                    "step_index": 1,
                    "type": "PLANNER_RESPONSE",
                    "thinking": "The user wants to create an Antigravity plugin for title management.",
                },
            ]
            with open(transcript_file, "w", encoding="utf-8") as f:
                for s in steps:
                    f.write(json.dumps(s) + "\n")

            ctx = extract_context(brain_dir, conv_id, existing_title="")
            self.assertEqual(ctx.primary_request, "设计一个 Antigravity 插件")
            self.assertEqual(len(ctx.assistant_summaries), 1)


if __name__ == "__main__":
    unittest.main()
