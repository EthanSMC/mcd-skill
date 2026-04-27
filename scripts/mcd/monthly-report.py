#!/usr/bin/env python3
"""月度消费报告"""
import sys, os, json, re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ORDERS_FILE, PREFS_FILE
from mcp import run_mcporter

def main():
    from datetime import datetime
    now = datetime.now()
    month_key = now.strftime("%Y-%m")
    month_name = now.strftime("%Y年%m月")

    # 账户信息
    account = run_mcporter("query-my-account")
    if "error" not in account:
        available = float(account.get("availablePoint", 0))
        expiring = float(account.get("currentMouthExpirePoint", 0))
        total_pts = float(account.get("accumulativePoint", 0))
        print(f"\n📊 {month_name} 麦当劳月度报告")
        print(f"   生成时间: {now.strftime('%Y-%m-%d %H:%M')}")
        print()
        print(f"💰 积分情况")
        print(f"   当前可用: {available:.1f} 分")
        print(f"   本月到期: {expiring:.1f} 分")
        print(f"   历史累计: {total_pts:.1f} 分")

    # 订单统计
    try:
        content = open(ORDERS_FILE, encoding="utf-8").read()
    except FileNotFoundError:
        print("\n📭 暂无历史订单")
        return

    month_orders = [b for b in content.split("## 订单 ") if b.startswith(month_key)]
    total_spent = 0
    order_count = len(month_orders)

    for block in month_orders:
        for line in block.split("\n"):
            m = re.search(r"¥([0-9.]+)", line)
            if m:
                total_spent += float(m.group(1))

    print()
    print(f"🛒 订单统计")
    print(f"   本月订单: {order_count} 笔")
    print(f"   本月消费: ¥{total_spent:.2f}")
    if order_count > 0:
        print(f"   客单价: ¥{total_spent/order_count:.2f}")

    # 历史累计
    all_orders = content.count("## 订单")
    print()
    print(f"📈 历史累计")
    print(f"   总订单: {all_orders} 笔")

except Exception as e:
    print(f"❌ 报告生成失败: {e}")

if __name__ == "__main__":
    main()
