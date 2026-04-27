#!/usr/bin/env python3
"""今日惊喜提醒"""
import sys, os
from config import *
from mcp import run_mcporter

def main():
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    data = run_mcporter("campaign-calendar")
    if "error" in data:
        print("❌ 获取活动失败")
        return

    today_events = []
    for day in data.get("dailyList", []):
        if day.get("date") == today:
            today_events = day.get("events", [])
            break

    if not today_events:
        print("🎁 今日暂无特别活动")
        return

    print(f"🎁 今日惊喜（{today}）")
    print()

    for event in today_events[:8]:
        article = event.get("articleDto", {})
        title = article.get("title", "").replace("📣", "").replace("🔥", "").strip()
        highlight = article.get("highlights", "")
        price = event.get("price", "")
        suffix = event.get("priceSuffix", "")

        if not title:
            continue

        tags = []
        if any(k in title for k in ["省", "元", "买", "送", "卡", "优惠"]):
            tags.append("💰")
        if any(k in title for k in ["新", "上线", "首发", "今", "登场"]):
            tags.append("🆕")
        if not tags:
            tags.append("⏰")

        price_str = f"（{price}{suffix}）" if price and price != "0" else ""
        print(f"  {' '.join(tags)} {title} {price_str}")

    print()
    print("告诉我想了解哪个，我帮你查价格！")

if __name__ == "__main__":
    main()
