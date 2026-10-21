"""
kasadin-Antigravity-title 单元测试: 校验器
"""

import unittest
from kasadin_antigravity_title.validator import (
    validate_title, parse_title, format_title, ALLOWED_EMOJIS
)


class TestValidator(unittest.TestCase):
    def test_valid_titles(self):
        samples = [
            "🧩 oil-codex-title｜本地部署与批量命名",
            "🎬 Seedance 2.0｜创作者创意选题与脚本规划",
            "🔎 AMD Radeon RX 9000｜价格与规格调研",
            "📝 安克AI黑客松｜参赛感想与复盘总结",
            "🎨 青花椒摄影｜8K微距静物提示词设计",
            "⚙️ 飞书CLI｜本地访问与配置联调",
            "📅 Q4产品迭代｜核心里程碑与任务拆解",
            "💬 人际沟通｜拒绝亲戚无理要求话术",
        ]
        for s in samples:
            valid, msg = validate_title(s)
            self.assertTrue(valid, f"Expected '{s}' to be valid, got: {msg}")

    def test_invalid_titles(self):
        # 缺少 emoji
        v, _ = validate_title("oil-codex-title｜本地部署")
        self.assertFalse(v)

        # 半角 |
        v, _ = validate_title("🧩 oil-codex-title|本地部署")
        self.assertFalse(v)

        # 多个 ｜
        v, _ = validate_title("🧩 oil-codex-title｜本地部署｜二次测试")
        self.assertFalse(v)

        # 换行符
        v, _ = validate_title("🧩 oil-codex-title｜本地部署\n后续")
        self.assertFalse(v)

        # 超出 48 字符
        v, _ = validate_title("🧩 " + "a" * 40 + "｜" + "b" * 10)
        self.assertFalse(v)

    def test_parse_title(self):
        res = parse_title("🎬 Seedance 2.0｜创作者创意选题与脚本规划")
        self.assertIsNotNone(res)
        emoji, category, obj, goal = res
        self.assertEqual(emoji, "🎬")
        self.assertEqual(category, "创意制作")
        self.assertEqual(obj, "Seedance 2.0")
        self.assertEqual(goal, "创作者创意选题与脚本规划")

    def test_format_title(self):
        res = format_title("🧩", "API模块", "接口鉴权与速率限制")
        self.assertEqual(res, "🧩 API模块｜接口鉴权与速率限制")


if __name__ == "__main__":
    unittest.main()
