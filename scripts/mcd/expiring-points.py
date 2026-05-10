#!/usr/bin/env python3
"""临期积分检查 + 最后一天自动兑换"""
import sys, os, re
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PREFS_FILE, DATA_DIR, mcd_err, is_last_day_of_month
from mcp_client import run_mcporter

def check_and_show():
    account = run_mcporter("query-my-account")
    if "error" in account:
        print(f"❌ 查询失败: {account['error']}")
        return

    available = float(account.get("availablePoint", 0))
    expiring = float(account.get("currentMouthExpirePoint", 0))

    print(f"\n📊 积分状态")
    print(f"   当前可用: {available:.1f} 分")
    print(f"   本月到期: {expiring:.1f} 分")

    if expiring == 0:
        print(f"\n   ✅ 本月无积分到期")
        return

    print(f"\n⚠️  {expiring:.0f} 积分即将到期（本月结束前）")

    mall = run_mcporter("mall-points-products pageSize=20")
    products = mall if isinstance(mall, list) else mall.get("data", [])
    if not products:
        print("   暂无积分商品")
        return

    # 解析+计算性价比
    affordable = []
    for p in products:
        try:
            points = float(p.get("point", 0))
            price_match = re.search(r"([0-9.]+)元", p.get("selling", ""))
            price = float(price_match.group(1)) if price_match else 0
            if points > 0 and price > 0:
                affordable.append({
                    **p,
                    "points": points,
                    "price": price,
                    "value": price / points * 100,
                })
        except: pass

    affordable.sort(key=lambda x: x["value"], reverse=True)
    best = affordable[0]
    print(f"\n🥇 最划算: {best.get('spuName')} | {best['points']:.0f}积分抵¥{best['price']:.1f}")

    cover = [p for p in affordable if p["points"] <= expiring]
    if cover:
        print(f"🎯 可cover到期积分的方案:")
        for p in cover[:5]:
            print(f"   • {p.get('spuName')} | {p['points']:.0f}积分抵¥{p['price']:.1f}")

def auto_redeem():
    """最后一天自动兑换"""
    if not is_last_day_of_month():
        print(f"📅 今天不是本月最后一天，跳过")
        return

    print(f"🔴 今天是本月最后一天，开始自动兑换...")

    account = run_mcporter("query-my-account")
    if "error" in account:
        mcd_err("自动兑换失败: " + account["error"])
        return

    expiring = float(account.get("currentMouthExpirePoint", 0))
    if expiring == 0:
        print("✅ 本月无积分到期，无需兑换")
        return

    mall = run_mcporter("mall-points-products pageSize=20")
    products = mall if isinstance(mall, list) else mall.get("data", [])
    if not products:
        mcd_err("无积分商品")
        return

    affordable = []
    for p in products:
        try:
            points = float(p.get("point", 0))
            price_match = re.search(r"([0-9.]+)元", p.get("selling", ""))
            price = float(price_match.group(1)) if price_match else 0
            if 0 < points <= expiring:
                affordable.append({**p, "points": points, "price": price, "value": price/points*100})
        except: pass

    if not affordable:
        print("❌ 无可兑换方案（所需积分均超过到期积分）")
        return

    best = sorted(affordable, key=lambda x: x["value"], reverse=True)[0]
    print(f"🚀 兑换: {best.get('spuName')} | {best['points']:.0f}积分抵¥{best['price']:.1f}")

    result = run_mcporter(f"mall-create-order skuId={best.get('skuId')} spuId={best.get('spuId')} shopId=2 points={int(best['points'])}")

    if "error" in result:
        mcd_err("兑换失败: " + result["error"])
        print(f"❌ 兑换失败")
    elif result.get("success"):
        print(f"✅ 兑换成功！")
    else:
        print(f"⚠️ 兑换结果: {result}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "auto-redeem":
        auto_redeem()
    else:
        check_and_show()
