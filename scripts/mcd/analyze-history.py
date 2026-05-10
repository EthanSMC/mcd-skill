#!/usr/bin/env python3
"""从历史订单分析口味偏好（满5单解锁）"""
import sys, os, json, re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ORDERS_FILE, PREFS_FILE, DATA_DIR

ITEM_TAGS = {
    "巨无霸": {"spicy": 0, "salty": 3, "sweet": 0, "meat": "beef"},
    "麦辣": {"spicy": 4, "salty": 2, "sweet": 0, "meat": "chicken"},
    "板烧": {"spicy": 1, "salty": 2, "sweet": 1, "meat": "chicken"},
    "麦香鱼": {"spicy": 0, "salty": 2, "sweet": 0, "meat": "fish"},
    "吉士": {"spicy": 0, "salty": 2, "sweet": 2, "meat": "beef"},
    "安格斯": {"spicy": 0, "salty": 3, "sweet": 0, "meat": "beef"},
}

def parse_orders():
    try:
        content = open(ORDERS_FILE, encoding="utf-8").read()
    except FileNotFoundError:
        return []
    orders = []
    for block in content.split("## 订单 ")[1:]:
        lines = block.strip().split("\n")
        order = {"items": [], "total": 0, "store": ""}
        for line in lines:
            if "门店 |" in line:
                order["store"] = line.split("|")[2].strip()
            elif "金额 |" in line:
                m = re.search(r"¥([0-9.]+)", line)
                if m: order["total"] = float(m.group(1))
            elif re.match(r"\| [^|]", line):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3 and parts[2] not in ("商品", "数量", ""):
                    qty_m = re.search(r"x(\d+)", line)
                    order["items"].append({"name": parts[2], "quantity": int(qty_m.group(1)) if qty_m else 1})
        if order["items"]:
            orders.append(order)
    return orders

def analyze(orders):
    if len(orders) < 5:
        return None, len(orders)

    tag_sum = {"spicy": [], "salty": [], "sweet": [], "meat": {}}
    item_freq = {}
    prices = []

    for o in orders:
        prices.append(o["total"])
        for item in o["items"]:
            name, qty = item["name"], item["quantity"]
            item_freq[name] = item_freq.get(name, 0) + qty
            for kw, tags in ITEM_TAGS.items():
                if kw in name:
                    if tags.get("spicy"): tag_sum["spicy"].append(tags["spicy"] * qty)
                    if tags.get("salty"): tag_sum["salty"].append(tags["salty"] * qty)
                    if tags.get("sweet"): tag_sum["sweet"].append(tags["sweet"] * qty)
                    if tags.get("meat"): tag_sum["meat"][tags["meat"]] = tag_sum["meat"].get(tags["meat"], 0) + qty

    avg = lambda lst: round(sum(lst)/len(lst)) if lst else 3
    spicy = max(1, min(5, avg(tag_sum["spicy"])))
    salty = max(1, min(5, avg(tag_sum["salty"])))
    sweet = max(1, min(5, avg(tag_sum["sweet"])))

    return {
        "orderCount": len(orders),
        "tasteProfile": {"spicy": spicy, "salty": salty, "sweet": sweet, "sour": 2},
        "avgPrice": round(sum(prices)/len(prices), 2),
        "topMeat": max(tag_sum["meat"], key=tag_sum["meat"].get) if tag_sum["meat"] else "beef",
        "topItems": sorted(item_freq.items(), key=lambda x: x[1], reverse=True)[:3],
    }, len(orders)

def main():
    orders = parse_orders()
    count = len(orders)
    print(f"📊 历史订单: {count} 笔")

    if count < 5:
        print(f"⏳ 偏好模块未解锁（还需 {5-count} 笔）")
        return

    profile, _ = analyze(orders)
    with open(PREFS_FILE, "r") as f:
        prefs = json.load(f)

    prefs["preferences"]["tasteProfile"] = profile["tasteProfile"]
    prefs["preferences"]["priceRange"] = {
        "min": max(20, profile["avgPrice"] * 0.7),
        "max": profile["avgPrice"] * 1.3,
    }
    prefs["notes"] = [f"从{count}笔历史订单分析得出"]

    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

    print(f"✅ 偏好已更新（{count}笔）")
    print(f"   口味: 辣{profile['tasteProfile']['spicy']} 咸{profile['tasteProfile']['salty']} 甜{profile['tasteProfile']['sweet']}")
    print(f"   均价: ¥{profile['avgPrice']}")

if __name__ == "__main__":
    main()
