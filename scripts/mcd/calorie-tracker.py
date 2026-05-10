#!/usr/bin/env python3
"""热量追踪"""
import sys, os, json, re
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CALORIES_FILE, DATA_DIR, parse_calories

def add_from_order(order_json_str):
    data = json.loads(order_json_str)
    items = data.get("items", [])
    if not items:
        return
    total_cal = sum(parse_calories(i.get("name", ""), i.get("quantity", 1)) for i in items)
    now = datetime.now()
    record = f"\n## {now.strftime('%Y-%m-%d')}\n- 时间: {now.strftime('%H:%M')}\n"
    record += f"- 门店: {data.get('storeName', '未知')}\n"
    record += f"- 总热量: ~{total_cal}kcal\n"
    for item in items:
        record += f"- {item.get('name')} x{item.get('quantity',1)}: ~{parse_calories(item.get('name',''), item.get('quantity',1))}kcal\n"
    os.makedirs(os.path.dirname(CALORIES_FILE), exist_ok=True)
    with open(CALORIES_FILE, "a", encoding="utf-8") as f:
        f.write(record)
    print(f"✅ 已记录: ~{total_cal}kcal | {len(items)}件商品")

def get_stats(date_str):
    try:
        content = open(CALORIES_FILE, encoding="utf-8").read()
    except FileNotFoundError:
        return 0
    blocks = [b for b in content.split("## ") if b.startswith(date_str)]
    total = 0
    for block in blocks:
        for line in block.split("\n"):
            if "总热量" in line:
                try:
                    total += int(line.split("~")[1].replace("kcal", "").strip())
                except:
                    pass
    return total

def show_report():
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_cal = get_stats(today_str)

    # 本周
    week_start = today - timedelta(days=today.weekday())
    week_cal = sum(get_stats((week_start + timedelta(days=i)).strftime("%Y-%m-%d")) for i in range(7))

    # 本月
    month_str = today.strftime("%Y-%m")
    month_cal = 0
    try:
        content = open(CALORIES_FILE, encoding="utf-8").read()
        month_cal = sum(int(l.split("~")[1].replace("kcal",""))
            for b in content.split("## ")
            if b.startswith(month_str)
            for l in b.split("\n") if "总热量" in l
        )
    except: pass

    print(f"\n🍔 热量追踪报告")
    print(f"📅 今日: ~{today_cal}kcal")
    if today_cal > 0:
        pct = min(100, today_cal / 2000 * 100)
        bar = "█" * int(pct/5) + "░" * (20 - int(pct/5))
        print(f"   [{bar}] {pct:.0f}% 日建议(2000kcal)")
    print(f"📆 本周: ~{week_cal}kcal")
    print(f"🗓️ 本月: ~{month_cal}kcal")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "add" and len(sys.argv) >= 3:
        add_from_order(sys.argv[2])
    else:
        show_report()
