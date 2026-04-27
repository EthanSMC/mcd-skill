#!/usr/bin/env python3
"""每日优惠券自动领取"""
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import mcd_log
from mcp import run_mcporter

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 优惠券检查")

    # 领取
    result = run_mcporter("auto-bind-coupons")
    if "error" in result:
        print(f"❌ 领券失败: {result['error']}")
        mcd_log(f"领券失败: {result['error']}")
        return

    success = result.get("successCount", 0)
    failed = result.get("failedCount", 0)
    coupons = result.get("successCoupons", [])

    if success > 0:
        print(f"✅ 领取成功: {success} 张")
        for c in coupons:
            print(f"   + {c.get('couponName', '优惠券')}")
        mcd_log(f"领取成功: {success} 张")
    else:
        print("ℹ️ 今日无新券可领")
        mcd_log("今日无新券")

if __name__ == "__main__":
    main()
