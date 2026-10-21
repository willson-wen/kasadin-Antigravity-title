"""
kasadin-Antigravity-title 单元测试: 引擎
"""

import unittest
from kasadin_antigravity_title.engine import generate_title, detect_category
from kasadin_antigravity_title.transcript_reader import ConversationContext
from kasadin_antigravity_title.validator import validate_title


class TestEngine(unittest.TestCase):
    def test_detect_category(self):
        self.assertEqual(detect_category("剪辑一个视频分镜脚本"), "🎬")
        self.assertEqual(detect_category("编写Python脚本开发一个插件"), "🧩")
        self.assertEqual(detect_category("调研市面上竞品价格与白皮书"), "🔎")
        self.assertEqual(detect_category("配置本地环境部署Docker服务"), "⚙️")
        self.assertEqual(detect_category("写一个复盘文档和学习总结"), "📝")

    def test_generate_title_from_context(self):
        ctx = ConversationContext(
            conversation_id="test-1",
            existing_title="AMD Radeon RX 9000 Pricing",
            user_requests=["AMD Radeon RX 9000多少钱？有哪些规格？"],
        )
        title = generate_title(ctx)
        is_valid, msg = validate_title(title)
        self.assertTrue(is_valid, f"Generated '{title}' failed validation: {msg}")
        self.assertIn("AMD Radeon RX 9000", title)

    def test_error_context_handling(self):
        ctx = ConversationContext(
            conversation_id="test-2",
            existing_title="",
            preview="报错排查",
            user_requests=["有bug"],
            has_error=True,
            assistant_summaries=["ERROR:mcp_server_git.server is not a valid Git repository"],
        )
        title = generate_title(ctx)
        is_valid, msg = validate_title(title)
        self.assertTrue(is_valid, f"Generated '{title}' failed validation: {msg}")
        self.assertTrue(title.startswith("⚙️"))


if __name__ == "__main__":
    unittest.main()
