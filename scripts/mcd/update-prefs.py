#!/usr/bin/env python3
"""偏好管理"""
import sys, os, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PREFS_FILE

def show():
    try:
        with open(PREFS_FILE) as f:
            prefs = json.load(f)
    except FileNotFoundError:
        print("📭 还未初始化，请先运行 onboarding.py")
        return
    p = prefs["preferences"]
    tp = p["tasteProfile"]
    print(f"\n📋 偏好档案（更新于 {prefs.get('updatedAt', '?')}）")
    print(f"   口味: 辣{tp['spicy']} 甜{tp['sweet']} 咸{tp['salty']} 酸{tp['sour']}（1-5分）")
    print(f"   预算: ¥{p['priceRange']['min']:.0f}-{p['priceRange']['max']:.0f}/次")
    print(f"   收藏: {len(p.get('favoriteItems', []))} 件")
    favs = p.get("favoriteItems", [])
    for f in favs:
        print(f"      - {f.get('name', f)}")
    print(f"   备注: {prefs.get('notes', ['无'])[0]}")

def update_taste(key, value):
    with open(PREFS_FILE) as f:
        prefs = json.load(f)
    labels = {"spicy": "辣", "sweet": "甜", "salty": "咸", "sour": "酸"}
    if key not in prefs["preferences"]["tasteProfile"]:
        print(f"❌ 未知口味: {key}")
        return
    value = max(1, min(5, int(value)))
    prefs["preferences"]["tasteProfile"][key] = value
    prefs["updatedAt"] = datetime.now().strftime("%Y-%m-%d")
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)
    print(f"✅ 已更新: {labels.get(key,key)} = {value}/5")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "show":
        show()
    elif cmd == "taste" and len(sys.argv) == 4:
        update_taste(sys.argv[2], sys.argv[3])
    else:
        print("用法:")
        print("  update-prefs.py show")
        print("  update-prefs.py taste spicy 4")
