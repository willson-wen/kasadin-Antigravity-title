"""
kasadin-Antigravity-title SQLite 数据库适配器
提供 conversation_summaries.db 的安全读取、原子备份、恢复以及标题同步更新（含 FTS 索引与 annotations 双向维护）
"""

import os
import re
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .validator import validate_title


class DBAdapter:
    def __init__(self, db_path: Path, backup_dir: Path, annotations_dir: Optional[Path] = None):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.annotations_dir = Path(annotations_dir or self.db_path.parent / "annotations")

    def _get_connection(self) -> sqlite3.Connection:
        if not self.db_path.exists():
            raise FileNotFoundError(f"未找到 Antigravity 数据库文件：{self.db_path}")
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def create_backup(self, tag: str = "auto") -> Path:
        """
        利用 SQLite 官方在线备份接口创建 ACID 一致性快照，并备份 annotations 文件夹
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"conversation_summaries_{timestamp}_{tag}.db"

        source_conn = self._get_connection()
        try:
            dest_conn = sqlite3.connect(str(backup_file))
            try:
                source_conn.backup(dest_conn)
            finally:
                dest_conn.close()
        finally:
            source_conn.close()

        # 备份对应的 annotations 目录
        if self.annotations_dir.exists():
            annotations_backup = self.backup_dir / f"annotations_{timestamp}_{tag}"
            try:
                shutil.copytree(str(self.annotations_dir), str(annotations_backup), dirs_exist_ok=True)
            except Exception:
                pass

        return backup_file

    def list_backups(self) -> List[Path]:
        """列出所有历史备份，按时间倒序排序"""
        if not self.backup_dir.exists():
            return []
        backups = list(self.backup_dir.glob("conversation_summaries_*.db"))
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return backups

    def restore_backup(self, backup_file: Path) -> bool:
        """从备份文件恢复数据库及对应的 annotations"""
        backup_file = Path(backup_file)
        if not backup_file.exists():
            raise FileNotFoundError(f"备份文件不存在：{backup_file}")

        # 恢复前先对当前状态进行保底备份
        self.create_backup(tag="pre_restore_safety")

        # 借助 SQLite backup API 恢复
        dest_conn = self._get_connection()
        try:
            source_conn = sqlite3.connect(str(backup_file))
            try:
                source_conn.backup(dest_conn)
            finally:
                source_conn.close()
        finally:
            dest_conn.close()

        # 恢复匹配的 annotations
        base_name = backup_file.stem.replace("conversation_summaries_", "annotations_")
        matched_annotations = self.backup_dir / base_name
        if matched_annotations.exists():
            try:
                shutil.copytree(str(matched_annotations), str(self.annotations_dir), dirs_exist_ok=True)
            except Exception:
                pass

        return True

    def get_stats(self) -> Dict[str, Any]:
        """获取会话与命名统计"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            total = cur.execute("SELECT COUNT(*) FROM conversation_summaries").fetchone()[0]
            top_query = "SELECT COUNT(*) FROM conversation_summaries WHERE parent_conversation_id = ''"
            top_level = cur.execute(top_query).fetchone()[0]
            subagents = total - top_level

            # 检查顶层会话命名合规度
            rows_query = (
                "SELECT conversation_id, title FROM conversation_summaries WHERE parent_conversation_id = ''"
            )
            rows = cur.execute(rows_query).fetchall()
            formatted_count = 0
            empty_count = 0
            unformatted_count = 0

            for r in rows:
                t = r["title"] or ""
                if not t.strip():
                    empty_count += 1
                else:
                    is_valid, _ = validate_title(t)
                    if is_valid:
                        formatted_count += 1
                    else:
                        unformatted_count += 1

            return {
                "total": total,
                "top_level": top_level,
                "subagents": subagents,
                "formatted": formatted_count,
                "unformatted": unformatted_count,
                "empty": empty_count,
            }
        finally:
            conn.close()

    def list_top_level_conversations(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取所有主界面显示的顶层会话（按最后修改时间倒序）"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            query = """
                SELECT conversation_id, title, preview, step_count, last_modified_time
                FROM conversation_summaries
                WHERE parent_conversation_id = ''
                ORDER BY last_modified_time DESC
            """
            if limit:
                query += f" LIMIT {int(limit)}"
            rows = cur.execute(query).fetchall()

            results = []
            for r in rows:
                cid = r["conversation_id"]
                fts_row = cur.execute(
                    "SELECT user_body FROM conversations_fts WHERE conversation_id = ? LIMIT 1",
                    (cid,)
                ).fetchone()
                fallback_body = fts_row["user_body"] if fts_row else ""

                results.append({
                    "conversation_id": cid,
                    "title": r["title"] or "",
                    "preview": r["preview"] or "",
                    "step_count": r["step_count"],
                    "last_modified_time": r["last_modified_time"],
                    "fallback_body": fallback_body,
                })
            return results
        finally:
            conn.close()

    def _sync_annotation_file(self, conversation_id: str, new_title: str) -> None:
        """更新 Antigravity 侧边栏实际读取的 annotations/<conv_id>.pbtxt 文件"""
        try:
            self.annotations_dir.mkdir(parents=True, exist_ok=True)
            pbtxt_file = self.annotations_dir / f"{conversation_id}.pbtxt"
            escaped = new_title.replace('"', '\\"')

            if pbtxt_file.exists():
                content = pbtxt_file.read_text(encoding="utf-8")
                if "title:" in content:
                    updated = re.sub(r'title:\".*?\"', f'title:"{escaped}"', content)
                else:
                    updated = f'title:"{escaped}" ' + content
                pbtxt_file.write_text(updated, encoding="utf-8")
            else:
                pbtxt_file.write_text(f'title:"{escaped}"\n', encoding="utf-8")
        except Exception:
            pass

    def update_conversation_title(self, conversation_id: str, new_title: str) -> Tuple[bool, str]:
        """
        更新会话标题：同时维护 conversation_summaries、conversations_fts 以及 annotations/*.pbtxt
        """
        is_valid, reason = validate_title(new_title)
        if not is_valid:
            return False, f"标题格式校验未通过: {reason}"

        conn = self._get_connection()
        try:
            cur = conn.cursor()

            # 1. 检查会话是否存在
            exists = cur.execute(
                "SELECT 1 FROM conversation_summaries WHERE conversation_id = ?",
                (conversation_id,)
            ).fetchone()
            if not exists:
                return False, f"未找到会话 ID: {conversation_id}"

            # 2. 更新主表 (同时维护 title 和 preview)
            cur.execute(
                "UPDATE conversation_summaries SET title = ?, preview = ? WHERE conversation_id = ?",
                (new_title, new_title, conversation_id)
            )

            # 3. 更新全文检索索引表（保持搜索一致）
            try:
                cur.execute(
                    "UPDATE conversations_fts SET title = ? WHERE conversation_id = ?",
                    (new_title, conversation_id)
                )
            except Exception:
                pass  # 如果 FTS 表不存在某些记录不阻断主更新

            conn.commit()

            # 4. 同步更新 Antigravity UI 直接读取渲染的 annotations 实体文件
            self._sync_annotation_file(conversation_id, new_title)

            return True, "更新成功"
        except Exception as e:
            conn.rollback()
            return False, f"更新异常: {str(e)}"
        finally:
            conn.close()
