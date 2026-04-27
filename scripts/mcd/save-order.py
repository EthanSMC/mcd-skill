#!/usr/bin/env python3
"""记录订单到历史文件（追加MD格式）"""
import sys, os, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PREFS_FILE, ORDERS_FILE, DATA_DIR
from mcp import run_mcporter

def save_order(order_data):
    now = datetime.now()
    items = order_data.get("items", [])
    total = order_data.get("total", 0)
    store = order_data.get("storeName", "未知门店")
    order_id = order_data.get("orderId", "")

    lines = [f"## 订单 {now.strftime('%Y-%m-%d %H:%M')}"]
    if order_id:
        lines.append(f"| 订单号 | `{order_id}` |")
    lines.append(f"| 门店 | {store} |")
    lines.append(f"| 金额 | ¥{total:.2f} |")
    lines.append(f"|")
    lines.append(f"| 商品 | 数量 |")
    lines.append(f"|:---|:---:|")
    for item in items:
        name = item.get("name", "未知")
        qty = item.get("quantity", 1)
        lines.append(f"| {name} | x{qty} |")

    entry = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(ORDERS_FILE), exist_ok=True)
    with open(ORDERS_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

    print(f"✅ 订单已记录: {store} | ¥{total:.2f} | {len(items)}件")

def show_history():
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("📭 暂无历史订单")
        return
    count = content.count("## 订单")
    print(f"📊 历史订单: {count} 笔 | {ORDERS_FILE}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_history()
    else:
        try:
            save_order(json.loads(sys.argv[1]))
        except json.JSONDecodeError:
            print("❌ JSON 解析失败")
