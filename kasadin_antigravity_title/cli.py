"""
kasadin-Antigravity-title 命令行入口
支持诊断、状态查看、会话列表、单条/批量预览与重命名，以及数据库自动备份与恢复
"""

import argparse
import sys
from pathlib import Path

from .config import Config
from .db_adapter import DBAdapter
from .engine import generate_title
from .transcript_reader import extract_context
from .validator import validate_title


def print_banner():
    print("=" * 60)
    print(" 🧩 kasadin-Antigravity-title ｜ 会话规范命名系统")
    print("=" * 60)


def cmd_doctor(args, cfg: Config, db: DBAdapter):
    print_banner()
    print("🔍 正在检查 Antigravity 环境...")

    ok = True
    print(f"  • Antigravity 数据目录: {cfg.antigravity_dir}")
    if cfg.antigravity_dir.exists():
        print("    [✓] 数据目录存在")
    else:
        print("    [✗] 数据目录不存在")
        ok = False

    print(f"  • 数据库路径: {cfg.db_path}")
    if cfg.db_path.exists():
        print(f"    [✓] 数据库就绪（文件大小: {cfg.db_path.stat().st_size // 1024} KB）")
    else:
        print("    [✗] 数据库未找到")
        ok = False

    print(f"  • Brain 会话轨迹目录: {cfg.brain_dir}")
    if cfg.brain_dir.exists():
        print(f"    [✓] Brain 目录存在（含 {len(list(cfg.brain_dir.glob('*')))} 个会话轨迹）")
    else:
        print("    [!] Brain 目录未找到（将依赖数据库 FTS 文本提取）")

    if ok:
        stats = db.get_stats()
        print("\n📊 基础统计：")
        print(f"  • 总会话数: {stats['total']}（侧边栏顶层会话: {stats['top_level']}，子 Agent: {stats['subagents']}）")
        print(f"  • 已规范命名: {stats['formatted']}")
        print(f"  • 未规范命名: {stats['unformatted']}")
        print(f"  • 空白无标题: {stats['empty']}")
        compliance = (stats['formatted'] / stats['top_level'] * 100) if stats['top_level'] else 0
        print(f"  • 规范覆盖率: {compliance:.1f}%\n")
        print("🎉 Antigravity 环境诊断通过，随时可执行命名与整理！")
    else:
        print("\n❌ 环境检查未通过，请确认 Antigravity 路径。")
        sys.exit(1)


def cmd_status(args, cfg: Config, db: DBAdapter):
    stats = db.get_stats()
    print_banner()
    print("📊 Antigravity 会话命名现状：")
    print(f"  • 侧边栏顶层会话数: {stats['top_level']}")
    print(f"  • 规范格式标题  : {stats['formatted']} 条")
    print(f"  • 待整理非标标题: {stats['unformatted']} 条")
    print(f"  • 待补充空白标题: {stats['empty']} 条")
    compliance = (stats['formatted'] / stats['top_level'] * 100) if stats['top_level'] else 0
    print(f"  • 规范覆盖率    : {compliance:.1f}%")

    backups = db.list_backups()
    print(f"\n💾 备份快照数: {len(backups)} 个")
    if backups:
        print(f"  • 最近备份: {backups[0].name}")


def cmd_list(args, cfg: Config, db: DBAdapter):
    convs = db.list_top_level_conversations(limit=args.limit)
    print_banner()
    print(f"📋 侧边栏会话列表（共 {len(convs)} 条）：\n")

    for i, c in enumerate(convs, 1):
        cid = c["conversation_id"]
        title = c["title"] or "<无标题>"
        is_valid, _ = validate_title(title)
        tag = "[✓ 已规范]" if is_valid else "[! 待整理]"
        mtime = c["last_modified_time"][:19]
        print(f"{i:2d}. {tag} {title}")
        print(f"    ID: {cid} | 修改时间: {mtime}")


def cmd_preview(args, cfg: Config, db: DBAdapter):
    convs = db.list_top_level_conversations()
    if args.conv_id:
        convs = [c for c in convs if c["conversation_id"].startswith(args.conv_id)]
        if not convs:
            print(f"❌ 未找到匹配的会话 ID: {args.conv_id}")
            return

    print_banner()
    print(f"👀 命名效果预览（共 {len(convs)} 条）：\n")

    for c in convs:
        cid = c["conversation_id"]
        old_title = c["title"] or "<无标题>"
        is_valid, _ = validate_title(old_title)
        if args.unformatted_only and is_valid:
            continue

        ctx = extract_context(
            cfg.brain_dir,
            cid,
            existing_title=c["title"],
            preview=c["preview"],
            fallback_user_body=c["fallback_body"],
        )
        new_title = generate_title(ctx)

        print(f"• ID: {cid[:8]}... ({c['last_modified_time'][:10]})")
        print(f"  原标题: {old_title}")
        print(f"  新标题: {new_title}\n")


def cmd_rename(args, cfg: Config, db: DBAdapter):
    convs = db.list_top_level_conversations()
    matched = [c for c in convs if c["conversation_id"].startswith(args.conv_id)]
    if not matched:
        print(f"❌ 未找到匹配的会话 ID: {args.conv_id}")
        return

    c = matched[0]
    cid = c["conversation_id"]
    old_title = c["title"] or "<无标题>"

    if args.title:
        new_title = args.title
    else:
        ctx = extract_context(
            cfg.brain_dir,
            cid,
            existing_title=c["title"],
            preview=c["preview"],
            fallback_user_body=c["fallback_body"],
        )
        new_title = generate_title(ctx)

    is_valid, reason = validate_title(new_title)
    if not is_valid:
        print(f"❌ 拟定标题不符合规范: {reason}")
        print(f"   拟定内容: {new_title}")
        return

    print_banner()
    print(f"会话 ID: {cid}")
    print(f"原标题 : {old_title}")
    print(f"新标题 : {new_title}")

    if args.apply:
        backup_file = db.create_backup(tag=f"rename_{cid[:8]}")
        print(f"💾 已自动创建安全快照: {backup_file.name}")
        success, msg = db.update_conversation_title(cid, new_title)
        if success:
            print("✅ 标题更新成功！Antigravity 侧边栏已同步。")
        else:
            print(f"❌ 更新失败: {msg}")
    else:
        print("\n💡 当前为预览模式。追加 `--apply` 参数以真正生效写入。")


def cmd_batch(args, cfg: Config, db: DBAdapter):
    convs = db.list_top_level_conversations(limit=args.limit)
    candidates = []

    for c in convs:
        old_title = c["title"] or ""
        is_valid, _ = validate_title(old_title)
        if args.unformatted_only and is_valid:
            continue
        candidates.append(c)

    print_banner()
    print(f"🚀 批量命名任务：共发现 {len(candidates)} 条目标会话")

    if not candidates:
        print("🎉 没有需要重命名的会话，所有标题均已符合规范！")
        return

    if args.apply:
        backup_file = db.create_backup(tag="batch_rename")
        print(f"💾 已执行前置全量备份: {backup_file.name}\n")

    success_count = 0
    fail_count = 0

    for i, c in enumerate(candidates, 1):
        cid = c["conversation_id"]
        old_title = c["title"] or "<无标题>"
        ctx = extract_context(
            cfg.brain_dir,
            cid,
            existing_title=c["title"],
            preview=c["preview"],
            fallback_user_body=c["fallback_body"],
        )
        new_title = generate_title(ctx)

        if args.apply:
            ok, msg = db.update_conversation_title(cid, new_title)
            if ok:
                success_count += 1
                status_icon = "✓"
            else:
                fail_count += 1
                status_icon = "✗"
            print(f"[{i}/{len(candidates)}] {status_icon} {old_title} -> {new_title}")
        else:
            print(f"[{i}/{len(candidates)}] (预览) {old_title} -> {new_title}")

    print("\n" + "=" * 60)
    if args.apply:
        print(f"🎉 批量命名完成！成功: {success_count} 条，失败: {fail_count} 条。")
    else:
        print("💡 以上为预览结果。追加 `--apply` 参数以执行真正更新。")


def cmd_backup(args, cfg: Config, db: DBAdapter):
    print_banner()
    backup_file = db.create_backup(tag="manual")
    print(f"✅ 成功创建 Antigravity 会话数据库快照：\n   {backup_file}")


def cmd_restore(args, cfg: Config, db: DBAdapter):
    print_banner()
    backups = db.list_backups()
    if not backups:
        print("❌ 未找到任何可用的备份快照。")
        return

    target = None
    if args.file:
        target = Path(args.file)
        if not target.exists():
            target = cfg.backup_dir / args.file
    else:
        target = backups[0]

    if not target.exists():
        print(f"❌ 备份文件不存在: {target}")
        return

    print(f"⚠️  准备从以下快照恢复数据库：\n   {target.name}")
    db.restore_backup(target)
    print("✅ 数据库恢复成功！")


def main():
    parser = argparse.ArgumentParser(
        prog="kasadin-title",
        description="kasadin-Antigravity-title: Antigravity 会话智能规范化命名系统",
    )
    subparsers = parser.add_subparsers(dest="command")

    # doctor
    subparsers.add_parser("doctor", help="检查 Antigravity 运行环境与数据库就绪状态")

    # status
    subparsers.add_parser("status", help="查看会话命名覆盖率与统计信息")

    # list
    p_list = subparsers.add_parser("list", help="列出顶层会话及其标题格式状态")
    p_list.add_argument("--limit", type=int, default=None, help="展示条数限制")

    # preview
    p_prev = subparsers.add_parser("preview", help="预览生成的会话标题")
    p_prev.add_argument("conv_id", nargs="?", default=None, help="会话 ID（前缀匹配即可）")
    p_prev.add_argument("--unformatted-only", action="store_true", default=False, help="仅预览非标会话")

    # rename
    p_ren = subparsers.add_parser("rename", help="对指定会话进行重命名")
    p_ren.add_argument("conv_id", help="会话 ID（前缀匹配即可）")
    p_ren.add_argument("--title", default=None, help="手动指定新标题")
    p_ren.add_argument("--apply", action="store_true", default=False, help="立即写入数据库生效")

    # batch
    p_bat = subparsers.add_parser("batch", help="批量重命名历史会话")
    p_bat.add_argument("--apply", action="store_true", default=False, help="立即写入数据库生效")
    p_bat.add_argument("--limit", type=int, default=None, help="单次处理数量上限")
    p_bat.add_argument("--unformatted-only", action="store_true", default=True, help="仅处理非标/空白会话")

    # backup
    subparsers.add_parser("backup", help="手动创建当前会话数据库的安全快照")

    # restore
    p_res = subparsers.add_parser("restore", help="从历史备份快照恢复会话数据库")
    p_res.add_argument("file", nargs="?", default=None, help="指定备份文件名（留空则恢复最近一次）")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    cfg = Config()
    cfg.ensure_dirs()
    db = DBAdapter(cfg.db_path, cfg.backup_dir, cfg.annotations_dir)

    cmd_map = {
        "doctor": cmd_doctor,
        "status": cmd_status,
        "list": cmd_list,
        "preview": cmd_preview,
        "rename": cmd_rename,
        "batch": cmd_batch,
        "backup": cmd_backup,
        "restore": cmd_restore,
    }

    handler = cmd_map.get(args.command)
    if handler:
        handler(args, cfg, db)


if __name__ == "__main__":
    main()
