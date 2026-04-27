#!/usr/bin/env python3
"""订单追踪"""
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp import run_mcporter

STATUS_MAP = {1:"已下单", 2:"已接单", 3:"制作中", 4:"骑手取餐", 5:"配送中", 6:"已送达", 7:"已完成"}

def main():
    if len(sys.argv) < 2:
        print("用法: track-order.py <34位订单号>")
        return
    order_id = sys.argv[1]
    if len(order_id) != 34:
        print("❌ 订单号必须是34位数字")
        return

    data = run_mcporter(f"query-order orderId={order_id}")
    if "error" in data or not data.get("success"):
        print(f"❌ 查询失败: {data.get('message', data.get('error', '?'))}")
        return

    order = data.get("data", {})
    store = order.get("storeName", "N/A")
    status = STATUS_MAP.get(order.get("status", 0), "未知")
    create_time = order.get("createTime", "N/A")
    rider = order.get("riderName", None)

    print(f"\n📦 订单详情")
    print(f"   门店: {store}")
    print(f"   状态: {status}")
    print(f"   下单: {create_time}")
    if rider:
        print(f"   骑手: {rider}")
    items = order.get("itemList", [])
    if items:
        print(f"\n🛒 商品清单")
        for item in items:
            print(f"   {item.get('quantity',1)}x {item.get('productName','N/A')}")
    print(f"\n⏰ 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
