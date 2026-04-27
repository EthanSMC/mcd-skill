#!/usr/bin/env python3
"""
McDonald's MCP 公共调用模块
被所有脚本 import 使用

用法:
  from mcp import run_mcporter, call_mcd
"""

import subprocess
import json
import os
import sys

# ── 导入配置 ──────────────────────────────────────
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

try:
    from config import MCP_TOKEN, MCP_URL, TOKEN_FILE, mcd_err
except ImportError:
    # 降级处理
    MCP_TOKEN = os.environ.get("MCD_MCP_TOKEN", "")
    MCP_URL = "https://mcp.mcd.cn/mcp-servers/mcd-mcp"
    def mcd_err(msg): pass

# ── MCP 调用 ──────────────────────────────────────
def run_mcporter(cmd, timeout=30):
    """
    执行 mcporter 命令
    cmd: str, mcporter 命令（不含 mcporter 前缀）
    返回: dict 或 {"error": str}
    """
    full_cmd = f"mcporter call mcdonalds.{cmd}" if not cmd.startswith("mcporter") else f"mcporter {cmd}"

    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout.strip()
        if not output:
            return {"error": result.stderr or "空响应"}
        return json.loads(output)
    except subprocess.TimeoutExpired:
        return {"error": "命令超时"}
    except json.JSONDecodeError:
        return {"error": f"JSON解析失败: {result.stdout[:100]}"}
    except Exception as e:
        return {"error": str(e)}

def call_mcd(method, **kwargs):
    """
    高级封装: mcporter call mcdonalds.<method> key=value ...

    示例:
        call_mcd("query-my-account")
        call_mcd("query-store-coupons", beCode="145058702", storeCode="1450587")
    """
    parts = [method]
    for k, v in kwargs.items():
        if isinstance(v, str):
            v = f'"{v}"' if " " in v else v
        elif isinstance(v, list):
            v = json.dumps(v)
        parts.append(f"{k}={v}")

    return run_mcporter(" ".join(parts))

# ── 工具函数 ──────────────────────────────────────
def is_last_day_of_month():
    """判断今天是否是本月最后一天"""
    from datetime import datetime, timedelta
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    return tomorrow.month != today.month

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
    return 300 * quantity  # 默认

def now_str():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")
