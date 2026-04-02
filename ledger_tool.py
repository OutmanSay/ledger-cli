#!/usr/bin/env python3
"""极简记账工具 — 供 OpenClaw agent 调用

用法：
    # 记一笔
    python3 ledger_tool.py add --amount 35 --category 餐饮 --note "午饭"
    python3 ledger_tool.py add --amount 18 --category 交通 --note "打车"

    # 查询
    python3 ledger_tool.py today                    # 今天花了多少
    python3 ledger_tool.py month                    # 本月汇总
    python3 ledger_tool.py month 2026-03            # 指定月汇总
    python3 ledger_tool.py recent                   # 最近 10 笔
    python3 ledger_tool.py category 餐饮            # 查某分类本月
    python3 ledger_tool.py search 奶茶              # 搜索备注
    python3 ledger_tool.py stats                    # 本月分类统计
    python3 ledger_tool.py year                     # 年度汇总
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "ledger.db"

# 分类映射：用户可能说的 → 标准分类
CATEGORY_ALIASES = {
    # 餐饮
    "餐饮": "食品酒水", "吃饭": "食品酒水", "早饭": "食品酒水", "午饭": "食品酒水",
    "晚饭": "食品酒水", "早餐": "食品酒水", "午餐": "食品酒水", "晚餐": "食品酒水",
    "外卖": "食品酒水", "饮料": "食品酒水", "咖啡": "食品酒水", "奶茶": "食品酒水",
    "零食": "食品酒水", "水果": "食品酒水", "买菜": "食品酒水",
    # 交通
    "交通": "行车交通", "打车": "行车交通", "地铁": "行车交通", "公交": "行车交通",
    "停车": "行车交通", "加油": "行车交通", "出行": "行车交通", "车费": "行车交通",
    # 购物/日用
    "购物": "居家物业", "买东西": "居家物业", "日用": "居家物业", "超市": "居家物业",
    "家用": "居家物业",
    # 娱乐
    "娱乐": "休闲娱乐", "玩": "休闲娱乐", "电影": "休闲娱乐", "游戏": "休闲娱乐",
    "旅游": "休闲娱乐",
    # 老婆花的
    "老婆": "人情往来", "慈善": "人情往来", "慈善捐助": "人情往来", "给老婆": "人情往来",
    # 孩子
    "孩子": "人情往来", "煎包": "人情往来", "七七": "人情往来", "给孩子": "人情往来",
    # 人情
    "送礼": "人情往来", "请客": "人情往来", "红包": "人情往来",
    # 医疗
    "医疗": "医疗保健", "看病": "医疗保健", "药": "医疗保健", "体检": "医疗保健",
    # 学习/数码
    "学习": "学习进修", "数码": "学习进修", "电子产品": "学习进修", "订阅": "学习进修",
    # 通讯
    "话费": "交流通讯", "手机费": "交流通讯", "网费": "交流通讯",
    # 衣服
    "衣服": "衣服饰品", "鞋": "衣服饰品", "穿": "衣服饰品",
    # 其他
    "其他": "其他杂项",
}

# 子分类推断
SUBCATEGORY_HINTS = {
    ("食品酒水", "早"): "早午晚餐",
    ("食品酒水", "午"): "早午晚餐",
    ("食品酒水", "晚"): "早午晚餐",
    ("食品酒水", "饭"): "早午晚餐",
    ("食品酒水", "外卖"): "早午晚餐",
    ("食品酒水", "咖啡"): "水果零食",
    ("食品酒水", "奶茶"): "水果零食",
    ("食品酒水", "零食"): "水果零食",
    ("食品酒水", "水果"): "水果零食",
    ("行车交通", "打车"): "打车租车",
    ("行车交通", "地铁"): "公共交通",
    ("行车交通", "公交"): "公共交通",
    ("行车交通", "停车"): "私家车费用",
    ("行车交通", "加油"): "私家车费用",
    ("人情往来", "老婆"): "慈善捐助",
    ("人情往来", "慈善"): "慈善捐助",
    ("人情往来", "孩子"): "孝敬家长",
    ("人情往来", "送礼"): "送礼请客",
    ("人情往来", "请客"): "送礼请客",
}


def get_conn():
    return sqlite3.connect(str(DB_PATH))


def resolve_category(raw: str) -> str:
    raw = raw.strip()
    return CATEGORY_ALIASES.get(raw, raw)


def guess_subcategory(category: str, note: str) -> str:
    for (cat, hint), subcat in SUBCATEGORY_HINTS.items():
        if cat == category and hint in note:
            return subcat
    return ""


def cmd_add(args):
    category = resolve_category(args.category)
    note = args.note or ""
    subcategory = args.subcategory or guess_subcategory(category, f"{args.category} {note}")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = args.date or now

    conn = get_conn()
    conn.execute(
        "INSERT INTO transactions (type, category, subcategory, amount, date, note, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("expense", category, subcategory, args.amount, date, note, "manual"),
    )
    conn.commit()
    conn.close()
    print(f"✅ 已记账: ¥{args.amount:.1f} [{category}] {note} ({date[:10]})")


def cmd_today(args):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_conn()
    rows = conn.execute(
        "SELECT category, amount, note, date FROM transactions WHERE type='expense' AND date LIKE ? ORDER BY date DESC",
        (f"{today}%",),
    ).fetchall()
    total = sum(r[1] for r in rows)
    print(f"📅 今日支出: ¥{total:.1f} ({len(rows)} 笔)")
    for cat, amt, note, dt in rows:
        t = dt[11:16] if len(dt) > 11 else ""
        print(f"  {t} ¥{amt:.1f} [{cat}] {note}")
    conn.close()


def cmd_month(args):
    if args.month:
        month = args.month
    else:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    rows = conn.execute(
        "SELECT category, SUM(amount), COUNT(*) FROM transactions WHERE type='expense' AND date LIKE ? GROUP BY category ORDER BY SUM(amount) DESC",
        (f"{month}%",),
    ).fetchall()
    total = sum(r[1] for r in rows)
    print(f"📊 {month} 月度汇总: ¥{total:,.1f}")
    for cat, amt, cnt in rows:
        pct = amt / total * 100 if total > 0 else 0
        print(f"  {cat}: ¥{amt:,.1f} ({cnt}笔, {pct:.0f}%)")
    conn.close()


def cmd_recent(args):
    n = args.n or 10
    conn = get_conn()
    rows = conn.execute(
        "SELECT category, amount, note, date FROM transactions WHERE type='expense' ORDER BY date DESC LIMIT ?",
        (n,),
    ).fetchall()
    print(f"📋 最近 {n} 笔:")
    for cat, amt, note, dt in rows:
        print(f"  {dt[:10]} ¥{amt:.1f} [{cat}] {note}")
    conn.close()


def cmd_category(args):
    category = resolve_category(args.cat)
    month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    rows = conn.execute(
        "SELECT amount, note, date FROM transactions WHERE type='expense' AND category=? AND date LIKE ? ORDER BY date DESC",
        (category, f"{month}%"),
    ).fetchall()
    total = sum(r[0] for r in rows)
    print(f"🏷️ {month} [{category}]: ¥{total:,.1f} ({len(rows)}笔)")
    for amt, note, dt in rows[:20]:
        print(f"  {dt[:10]} ¥{amt:.1f} {note}")
    conn.close()


def cmd_search(args):
    conn = get_conn()
    rows = conn.execute(
        "SELECT category, amount, note, date FROM transactions WHERE type='expense' AND (note LIKE ? OR category LIKE ? OR subcategory LIKE ?) ORDER BY date DESC LIMIT 20",
        (f"%{args.keyword}%", f"%{args.keyword}%", f"%{args.keyword}%"),
    ).fetchall()
    print(f"🔍 搜索 '{args.keyword}': {len(rows)} 条")
    for cat, amt, note, dt in rows:
        print(f"  {dt[:10]} ¥{amt:.1f} [{cat}] {note}")
    conn.close()


def cmd_stats(args):
    month = datetime.now().strftime("%Y-%m")
    conn = get_conn()

    # 本月总计
    total = conn.execute(
        "SELECT SUM(amount) FROM transactions WHERE type='expense' AND date LIKE ?",
        (f"{month}%",),
    ).fetchone()[0] or 0

    # 日均
    day = datetime.now().day
    daily_avg = total / day if day > 0 else 0

    # 上月同期对比
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    last_total = conn.execute(
        "SELECT SUM(amount) FROM transactions WHERE type='expense' AND date LIKE ? AND CAST(SUBSTR(date, 9, 2) AS INTEGER) <= ?",
        (f"{last_month}%", day),
    ).fetchone()[0] or 0

    print(f"📈 {month} 统计")
    print(f"  本月总计: ¥{total:,.1f}")
    print(f"  日均: ¥{daily_avg:,.1f}")
    print(f"  上月同期: ¥{last_total:,.1f}")
    if last_total > 0:
        change = (total - last_total) / last_total * 100
        print(f"  同比: {'↑' if change > 0 else '↓'}{abs(change):.0f}%")
    conn.close()


def cmd_year(args):
    year = args.year or datetime.now().strftime("%Y")
    conn = get_conn()
    rows = conn.execute(
        "SELECT SUBSTR(date, 1, 7) as m, SUM(amount) FROM transactions WHERE type='expense' AND date LIKE ? GROUP BY m ORDER BY m",
        (f"{year}%",),
    ).fetchall()
    total = sum(r[1] for r in rows)
    print(f"📅 {year} 年度: ¥{total:,.1f}")
    for m, amt in rows:
        print(f"  {m}: ¥{amt:,.1f}")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="极简记账工具")
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add", help="记一笔")
    p_add.add_argument("--amount", "-a", type=float, required=True)
    p_add.add_argument("--category", "-c", required=True)
    p_add.add_argument("--subcategory", "-s", default="")
    p_add.add_argument("--note", "-n", default="")
    p_add.add_argument("--date", "-d", default="")

    p_today = sub.add_parser("today", help="今日支出")

    p_month = sub.add_parser("month", help="月度汇总")
    p_month.add_argument("month", nargs="?", default="")

    p_recent = sub.add_parser("recent", help="最近N笔")
    p_recent.add_argument("-n", type=int, default=10)

    p_cat = sub.add_parser("category", help="查分类")
    p_cat.add_argument("cat")

    p_search = sub.add_parser("search", help="搜索")
    p_search.add_argument("keyword")

    p_stats = sub.add_parser("stats", help="本月统计")

    p_year = sub.add_parser("year", help="年度汇总")
    p_year.add_argument("year", nargs="?", default="")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    cmds = {
        "add": cmd_add, "today": cmd_today, "month": cmd_month,
        "recent": cmd_recent, "category": cmd_category, "search": cmd_search,
        "stats": cmd_stats, "year": cmd_year,
    }
    cmds[args.cmd](args)


if __name__ == "__main__":
    main()
