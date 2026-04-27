#!/bin/bash
# McDonald's Skill 框架检测 + 路径配置
# 被所有脚本 source使用
# 用法: source "$(dirname "$0")/config.sh"

# ── 自动检测框架 ──────────────────────────────────
_detect_framework() {
  if [ -n "$OPENCLAW_WORKSPACE" ]; then
    FRAMEWORK="openclaw"
    WORKSPACE_DIR="$OPENCLAW_WORKSPACE"
  elif [ -n "$CLAUDE_CODE_DIR" ]; then
    FRAMEWORK="claude_code"
    WORKSPACE_DIR="$CLAUDE_CODE_DIR"
  elif [ -n "$AGENTS_WORKSPACE" ]; then
    FRAMEWORK="agents"
    WORKSPACE_DIR="$AGENTS_WORKSPACE"
  elif [ -n "$WORKSPACE" ]; then
    FRAMEWORK="generic"
    WORKSPACE_DIR="$WORKSPACE"
  else
    # 默认：脚本所在目录的父目录
    FRAMEWORK="local"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    WORKSPACE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
  fi
}

# ── 路径设置 ──────────────────────────────────────
_setup_paths() {
  SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

  DATA_DIR="${SKILL_ROOT}/data"
  SCRIPTS_DIR="${SKILL_ROOT}/scripts/mcd"
  DOCS_DIR="${SKILL_ROOT}/docs"

  # 数据文件
  PREFS_FILE="${DATA_DIR}/mcd-preferences.json"
  ORDERS_FILE="${DATA_DIR}/mcd-orders.md"
  CALORIES_FILE="${DATA_DIR}/mcd-calories.md"

  # 配置文件（用户token等）
  TOKEN_FILE="${DATA_DIR}/.mcd-token"

  # 日志目录
  LOGS_DIR="${SKILL_ROOT}/logs"
  mkdir -p "$LOGS_DIR" "$DATA_DIR"
}

# ── MCP Server 配置 ───────────────────────────────
_setup_mcp() {
  # 从文件读取 token（优先级）或环境变量
  if [ -f "$TOKEN_FILE" ]; then
    export MCP_TOKEN="$(cat "$TOKEN_FILE")"
  elif [ -n "$MCD_MCP_TOKEN" ]; then
    export MCP_TOKEN="$MCD_MCP_TOKEN"
  fi

  # 默认 MCP Server URL（通常不需要改）
  : "${MCD_MCP_URL:=https://mcp.mcd.cn/mcp-servers/mcd-mcp}"
}

# ── 初始化 ────────────────────────────────────────
_detect_framework
_setup_paths
_setup_mcp

# ── 便捷函数 ──────────────────────────────────────
mcd_log() {
  echo "[$(date '+%Y-%m-%d %H:%M')] $*" >> "${LOGS_DIR}/mcd.log"
}

mcd_err() {
  echo "[$(date '+%Y-%m-%d %H:%M')] ERROR: $*" >&2
  echo "[$(date '+%Y-%m-%d %H:%M')] ERROR: $*" >> "${LOGS_DIR}/mcd-error.log"
}

mcd_check_token() {
  if [ -z "$MCP_TOKEN" ]; then
    echo "❌ Token 未配置"
    echo ""
    echo "请先配置 Token："
    echo "  echo '你的Token' > $TOKEN_FILE"
    echo ""
    echo "或设置环境变量："
    echo "  export MCD_MCP_TOKEN='你的Token'"
    return 1
  fi
  return 0
}
