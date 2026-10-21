"""
kasadin-Antigravity-title 单元测试: 数据库适配器与备份恢复
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from kasadin_antigravity_title.db_adapter import DBAdapter


class TestDBAdapter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_summaries.db"
        self.backup_dir = Path(self.temp_dir.name) / "backups"

        # 创建测试 SQLite 数据库
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE conversation_summaries (
                conversation_id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '',
                preview TEXT NOT NULL DEFAULT '',
                step_count INTEGER NOT NULL DEFAULT 0,
                last_modified_time DATETIME NOT NULL,
                parent_conversation_id TEXT NOT NULL DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE VIRTUAL TABLE conversations_fts USING fts5(
                conversation_id UNINDEXED,
                title,
                user_body
            )
        """)
        conn.execute(
            "INSERT INTO conversation_summaries VALUES ('c1', '旧标题', '内容预览', 5, '2026-10-21 00:00:00', '')"
        )
        conn.execute(
            "INSERT INTO conversations_fts VALUES ('c1', '旧标题', '用户需求详情')"
        )
        conn.commit()
        conn.close()

        self.adapter = DBAdapter(self.db_path, self.backup_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_backup_and_restore(self):
        backup_file = self.adapter.create_backup(tag="test")
        self.assertTrue(backup_file.exists())

        backups = self.adapter.list_backups()
        self.assertEqual(len(backups), 1)

        # 修改原始数据库
        ok, _ = self.adapter.update_conversation_title("c1", "🧩 测试模块｜功能开发")
        self.assertTrue(ok)

        # 验证修改
        convs = self.adapter.list_top_level_conversations()
        self.assertEqual(convs[0]["title"], "🧩 测试模块｜功能开发")

        # 从备份恢复
        res = self.adapter.restore_backup(backup_file)
        self.assertTrue(res)

        # 验证已还原
        convs_restored = self.adapter.list_top_level_conversations()
        self.assertEqual(convs_restored[0]["title"], "旧标题")


if __name__ == "__main__":
    unittest.main()
