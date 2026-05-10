#!/usr/bin/env python3
"""
McDonald's MCP 公共调用模块
用法:
  from mcp_client import run_mcporter, call_mcd
"""

import subprocess
import json
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

try:
    from config import MCP_TOKEN, MCP_URL, TOKEN_FILE, mcd_err
except ImportError:
    MCP_TOKEN = os.environ.get("MCD_MCP_TOKEN", "")
    MCP_URL = "https://mcp.mcd.cn/mcp-servers/mcd-mcp"
    def mcd_err(msg): pass


def run_mcporter(cmd, timeout=30):
    """执行 mcporter 命令，返回 dict 或 {"error": str}"""
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
    """高级封装: mcporter call mcdonalds.<method> key=value ..."""
    parts = [method]
    for k, v in kwargs.items():
        if isinstance(v, str):
            v = f'"{v}"' if " " in v else v
        elif isinstance(v, list):
            v = json.dumps(v)
        parts.append(f"{k}={v}")
    return run_mcporter(" ".join(parts))
