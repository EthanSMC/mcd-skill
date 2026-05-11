#!/usr/bin/env python3
"""
McDonald's Skill 配置 - Python版
自动检测运行框架，设置相对路径
被所有脚本 import 使用

用法:
  from config import *
"""

import os
import sys
from pathlib import Path

# ── 框架检测 ─────────────────────────────────────
def _detect_framework():
    """检测当前运行的框架，设置 WORKSPACE_DIR"""
    if os.environ.get("OPENCLAW_WORKSPACE"):
        return os.environ["OPENCLAW_WORKSPACE"], "openclaw"
    elif os.environ.get("CLAUDE_CODE_DIR"):
        return os.environ["CLAUDE_CODE_DIR"], "claude_code"
    elif os.environ.get("AGENTS_WORKSPACE"):
        return os.environ["AGENTS_WORKSPACE"], "agents"
    elif os.environ.get("WORKSPACE"):
        return os.environ["WORKSPACE"], "generic"
    else:
        # 默认：脚本所在目录的父目录的父目录
        script_dir = Path(__file__).resolve().parent  # .../mcd-skill/scripts/mcd
        skill_root = script_dir.parent.parent          # .../mcd-skill
        return str(skill_root), "local"

WORKSPACE_DIR, FRAMEWORK = _detect_framework()

# ── 路径设置（相对于 WORKSPACE_DIR）───────────────
SKILL_ROOT = os.environ.get("SKILL_ROOT", WORKSPACE_DIR)

DATA_DIR    = os.path.join(WORKSPACE_DIR, "data")
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts", "mcd") if SKILL_ROOT != WORKSPACE_DIR else os.path.join(WORKSPACE_DIR, "scripts", "mcd")
DOCS_DIR    = os.path.join(SKILL_ROOT, "docs") if SKILL_ROOT != WORKSPACE_DIR else os.path.join(WORKSPACE_DIR, "docs")
LOGS_DIR    = os.path.join(WORKSPACE_DIR, "logs")

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ── 数据文件路径 ─────────────────────────────────
PREFS_FILE    = os.path.join(DATA_DIR, "mcd-preferences.json")
ORDERS_FILE   = os.path.join(DATA_DIR, "mcd-orders.md")
CALORIES_FILE = os.path.join(DATA_DIR, "mcd-calories.md")
TOKEN_FILE    = os.path.join(DATA_DIR, ".mcd-token")
COUPON_LOG    = os.path.join(LOGS_DIR, "mcd-coupon.log")
POINTS_LOG    = os.path.join(LOGS_DIR, "mcd-points.log")
ERROR_LOG     = os.path.join(LOGS_DIR, "mcd-error.log")

# ── MCP 配置 ─────────────────────────────────────
MCP_TOKEN = os.environ.get("MCD_MCP_TOKEN", "")
if not MCP_TOKEN and os.path.exists(TOKEN_FILE):
    MCP_TOKEN = open(TOKEN_FILE).read().strip()

MCP_URL = os.environ.get("MCD_MCP_URL", "https://open.mcd.cn/mcp-servers/mcd-mcp")

# ── 便捷函数 ──────────────────────────────────────
def mcd_log(msg):
    """写入日志"""
    with open(COUPON_LOG, "a") as f:
        f.write(f"[{_now()}] {msg}\n")

def mcd_err(msg):
    """写入错误日志"""
    with open(ERROR_LOG, "a") as f:
        f.write(f"[{_now()}] ERROR: {msg}\n")

def mcd_check_token():
    """检查 token 是否配置"""
    if not MCP_TOKEN:
        print("❌ Token 未配置！")
        print()
        print(f"请先配置 Token：")
        print(f"  echo '你的Token' > {TOKEN_FILE}")
        print()
        print("或设置环境变量：")
        print("  export MCD_MCP_TOKEN='你的Token'")
        print()
        print("如何获取 Token：")
        print("  1. 打开麦当劳 App 登录账号")
        print("  2. 访问 open.mcd.cn/mcp 官网扫码授权")
        print("  3. 复制 Token，粘贴到上面命令行")
        return False
    return True

def _now():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ── 工具函数 ──────────────────────────────────────
def parse_calories(item_name, quantity=1):
    """估算商品热量（千卡）"""
    CALORIE_ESTIMATE = {
        "巨无霸": 560, "麦辣": 490, "板烧": 430, "麦香鱼": 380,
        "吉士": 310, "安格斯": 680, "薯条": 330, "中薯": 330,
        "大薯": 460, "鸡翅": 290, "鸡块": 280, "可乐": 150,
        "中可": 150, "大可": 210, "雪冰": 180, "菠萝雪冰": 200,
        "苹果派": 220, "圆筒": 130, "甜筒": 130, "麦旋风": 270,
        "小食自由拼": 350,
    }
    for keyword, cal in CALORIE_ESTIMATE.items():
        if keyword in item_name:
            return cal * quantity
    return 300 * quantity


def now_str():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def is_last_day_of_month():
    """判断今天是否是本月最后一天"""
    from datetime import datetime, timedelta
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    return tomorrow.month != today.month
