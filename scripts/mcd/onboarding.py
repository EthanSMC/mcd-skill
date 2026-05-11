#!/usr/bin/env python3
"""
McDonald's Skill 首次引导流程
自动检测框架 + Token检查 + 初始化

用法:
  python3 onboarding.py
"""
import json
import sys
import os
from datetime import datetime

# 导入配置（自动检测路径）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *
from mcp_client import run_mcporter

# ── Token 配置步骤（新增）──────────────────────────
def step0_token_setup():
    """Step 0: 检查并引导配置 Token"""
    print("🔑 McDonald's Skill 配置向导")
    print("=" * 40)
    print()

    if MCP_TOKEN:
        print(f"✅ 已检测到 Token: {MCP_TOKEN[:8]}...{MCP_TOKEN[-4:]}")
        print(f"   存储位置: {TOKEN_FILE}")
        print()
        # 验证 token 是否有效
        account, _ = run_mcporter("mcporter call mcdonalds.query-my-account")
        if "error" not in account:
            print("   Token 验证通过 ✅")
            return True
        print("   ⚠️ Token 已失效，需要重新配置")
        print()

    print("📋 Token 配置指南:")
    print("   1. 打开麦当劳 App，登录你的账号")
    print("   2. 访问 https://open.mcd.cn/mcp 官网")
    print("   3. 扫码授权，获取 Token")
    print("   4. 复制 Token，粘贴到这里")
    print()
    print("请输入你的 Token（格式 xxxx-xxxx-xxxx）：")
    token = input("> ").strip()

    if not token or len(token) < 10:
        print("❌ Token 无效，已取消")
        return False

    # 保存 token
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

    # 更新全局变量
    globals()["MCP_TOKEN"] = token
    print(f"✅ Token 已保存到: {TOKEN_FILE}")
    print()

    # 验证
    account, err = run_mcporter("mcporter call mcdonalds.query-my-account")
    if "error" in account:
        print(f"⚠️ Token 验证失败: {account.get('error', err)[:100]}")
        return False

    print("✅ Token 验证通过！")
    return True

def step0_verify_token():
    """验证 token 是否有效（静默版，引导内使用）"""
    if not MCP_TOKEN:
        return False
    account, _ = run_mcporter("mcporter call mcdonalds.query-my-account")
    return "error" not in account

def step1_welcome():
    print("🍔 欢迎使用 McDonald's 点餐助手!")
    print("=" * 40)
    print("我来帮你完成初始设置，大约需要 2 分钟")
    print()

def step2_account():
    print("📊 正在查询账户状态...")
    account, err = run_mcporter("mcporter call mcdonalds.query-my-account")
    if "error" in account:
        print(f"⚠️ 账户查询失败: {err}")
        return None

    points = account.get("availablePoint", "N/A")
    expire = account.get("currentMouthExpirePoint", "N/A")
    total = account.get("accumulativePoint", "N/A")
    member_id = account.get("accountId", "")

    print(f"✅ 账户信息:")
    print(f"   当前积分: {points}")
    print(f"   本月到期: {expire}")
    print(f"   历史累计: {total}")
    return {"points": points, "expire": expire, "total": total, "member_id": member_id, "raw": account}

def step3_bind_coupons():
    print("\n🎫 正在自动领取优惠券...")
    coupons, err = run_mcporter("mcporter call mcdonalds.auto-bind-coupons")
    if "error" in coupons:
        print(f"⚠️ 领券失败: {err}")
    else:
        success = coupons.get("successCount", 0)
        failed = coupons.get("failedCount", 0)
        if success > 0:
            print(f"✅ 成功领取 {success} 张:")
            for c in coupons.get("successCoupons", []):
                print(f"   + {c.get('couponName', '优惠券')}")
        if failed > 0:
            print(f"⚠️ 失败 {failed} 张")
        if success == 0 and failed == 0:
            print("ℹ️ 今日无新券可领")

def step4_delivery_address():
    print("\n📍 正在查询配送地址...")
    addrs, err = run_mcporter("mcporter call mcdonalds.delivery-query-addresses beType=2")
    if "error" in addrs:
        print(f"⚠️ 地址查询失败: {err}")
        return []

    addresses = addrs.get("addresses", [])
    if addresses:
        print(f"✅ 找到 {len(addresses)} 个配送地址:")
        for i, addr in enumerate(addresses[:5], 1):
            print(f"   {i}. {addr.get('storeName', '未知门店')}")
            print(f"      {addr.get('fullAddress', '')}")
    else:
        print("⚠️ 未找到配送地址")
    return addresses

def step5_taste_prefs():
    print("\n🍽️ 口味偏好设置（可选）")
    print("请告诉我你的口味（1-5分，1=不喜欢，5=非常喜欢）")
    print("   直接回车使用默认值")
    print()

    taste = {"spicy": 3, "sweet": 3, "salty": 4, "sour": 2}
    labels_cn = {"spicy": "辣", "sweet": "甜", "salty": "咸", "sour": "酸"}

    print("📋 默认值:")
    for k, v in taste.items():
        bar = "★" * v + "☆" * (5 - v)
        print(f"   {labels_cn[k]}: {bar} ({v}/5)")

    print()
    print("💡 稍后可随时修改:")
    print(f"   python3 {__file__} taste")
    print()
    return taste

def step6_save_profile(taste, addresses, account_info=None):
    prefs = {
        "version": "1.0",
        "updatedAt": datetime.now().strftime("%Y-%m-%d"),
        "user": {
            "name": "",
            "memberId": ""
        },
        "preferences": {
            "priceRange": {"min": 30, "max": 60},
            "tasteProfile": taste,
            "favoriteItems": [],
            "dislikedItems": [],
            "dietaryRestrictions": [],
            "preferredStore": addresses[0] if addresses else {},
            "deliveryAddress": addresses[0] if addresses else {},
            "orderType": 2
        },
        "orderHistory": [],
        "monthlyStats": {},
        "notes": ["首次引导初始化"]
    }

    if account_info and "member_id" in account_info:
        prefs["user"]["memberId"] = account_info["member_id"]

    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

    print(f"✅ 偏好档案已保存: {PREFS_FILE}")

def step7_summary():
    print("\n" + "=" * 40)
    print("🎉 引导完成!")
    print("=" * 40)
    print()
    print("📌 开始使用:")
    print("   说「点麦当劳」开始点餐")
    print("   说「查积分」查看账户")
    print("   说「有什么优惠」查看今日活动")
    print()
    print(f"📁 数据文件: {DATA_DIR}/")
    print(f"   mcd-preferences.json - 你的偏好")
    print(f"   mcd-orders.md - 历史订单")
    print()

def main():
    # 检查是否已初始化
    if os.path.exists(PREFS_FILE):
        print("[McDonald's Skill]")
        print("ℹ️ 已检测到偏好档案，跳过引导")
        print(f"   路径: {PREFS_FILE}")
        print()
        print("如需重新引导，删除该文件后重新运行")
        print(f"   rm {PREFS_FILE}")
        return

    # Step 0: Token 配置
    token_ok = step0_token_setup()
    if not token_ok:
        print("=" * 40)
        print("⛔ Token 配置失败，无法继续")
        print("请重新运行: python3 onboarding.py")
        print("=" * 40)
        return

    step1_welcome()
    account_info = step2_account()
    step3_bind_coupons()
    addresses = step4_delivery_address()
    taste = step5_taste_prefs()
    step6_save_profile(taste, addresses, account_info)
    step7_summary()

if __name__ == "__main__":
    main()
