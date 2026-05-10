#!/usr/bin/env python3
"""Smart Combo 推荐器 - 3个方案供选择"""
import sys, os, json
from config import PREFS_FILE

PLANS = [
    {
        "name": "省钱饱腹",
        "budget": "25-40",
        "desc": "小食自由拼 + 任意饮料",
        "items": [{"name": "小食自由拼", "code": "9900014160", "qty": 1}],
        "tags": ["性价比", "灵活"],
    },
    {
        "name": "经典搭配",
        "budget": "40-55",
        "desc": "巨无霸大套餐",
        "items": [{"name": "巨无霸大套餐", "code": "9900003007", "qty": 1}],
        "tags": ["经典", "牛肉"],
    },
    {
        "name": "大口过瘾",
        "budget": "55-70",
        "desc": "板烧鸡腿堡四件套",
        "items": [{"name": "板烧四件套", "code": "9900014005", "qty": 1}],
        "tags": ["量大", "鸡肉", "不辣"],
    },
]

def get_budget():
    try:
        with open(PREFS_FILE) as f:
            prefs = json.load(f)
        pr = prefs.get("preferences", {}).get("priceRange", {})
        return pr.get("min", 30), pr.get("max", 60)
    except:
        return 30, 60

def get_taste():
    try:
        with open(PREFS_FILE) as f:
            prefs = json.load(f)
        return prefs.get("preferences", {}).get("tasteProfile", {"spicy": 3})
    except:
        return {"spicy": 3}

def main():
    min_b, max_b = get_budget()
    taste = get_taste()

    plans = [p for p in PLANS]
    if taste.get("spicy", 3) >= 4:
        plans = sorted(plans, key=lambda x: bool("不辣" in str(x.get("tags", []))))

    print(f"\n🍔 Smart Combo（预算 ¥{min_b:.0f}-{max_b:.0f}）")
    print(f"   口味: 辣{taste.get('spicy', '?')} 咸{taste.get('salty', '?')} 甜{taste.get('sweet', '?')}")
    print()
    for i, plan in enumerate(plans, 1):
        tags = " ".join(f"[{t}]" for t in plan.get("tags", []))
        print(f"   {i}. **{plan['name']}** {tags}")
        print(f"      {plan['desc']} | ¥{plan['budget']}")
        print()

if __name__ == "__main__":
    main()
