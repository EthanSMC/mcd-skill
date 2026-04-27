# McDonald's 点餐助手 Skill

> 🤖 装上就能用，零配置完成麦当劳外卖完全场景。支持 OpenClaw / Claude Code / Pi / Codex 等 Agent 框架。

[[reply_to_current]]

---

## 🎯 功能一览

| 功能 | 说明 | 自动/手动 |
|:---|:---|:---:|
| 🍔 惊喜提醒 | 点餐前展示今日省钱/新品/限时活动 | 自动 |
| 🛒 Smart Combo | 满5单后3个方案供选择 | 满5单解锁 |
| 💰 临期积分自动兑换 | 本月最后一天自动兑换最优方案 | 自动 |
| 🔥 热量追踪 | 记录每日/周/月摄入热量 | 自动 |
| 🎫 自动领券 | 每天9点自动领取优惠券 | 自动 |
| 📊 口味偏好学习 | 从历史订单分析口味（满5单） | 满5单解锁 |
| 🚴 订单追踪 | 报订单号查状态 | 手动 |

---

## ⚡ 快速安装

### 1. 前置要求

```bash
# 安装 mcporter（MCP Server 管理工具）
npm install -g mcporter

# 配置麦当劳 MCP Server
mcporter server add mcdonalds \
  --header "Authorization=Bearer YOUR_TOKEN" \
  --url "https://mcp.mcd.cn/mcp-servers/mcd-mcp"
```

### 2. 获取 Token

1. 打开 **麦当劳 App**，登录你的账号
2. 访问 **[mcp.mcd.cn](https://mcp.mcd.cn)** 官网
3. 扫码授权，获取 Token（格式 `xxxx-xxxx-xxxx`）
4. 将 Token 写入本地配置：

```bash
# 方式A：写入配置文件（脚本自动读取）
mkdir -p data
echo "你的Token" > data/.mcd-token

# 方式B：设置环境变量
export MCD_MCP_TOKEN="你的Token"
```

### 3. 启动引导

```bash
python3 scripts/mcd/onboarding.py
```

引导会自动完成：
- ✅ Token 验证
- ✅ 领取所有可领券
- ✅ 查询配送地址
- ✅ 初始化偏好档案

---

## 🚀 立即使用

### 用户（人类）

直接对我说：

```
点麦当劳
有什么优惠
查一下我的积分
帮我追踪订单 1030938730000733964700499858
改一下，我不吃辣
```

### Agent（AI 助手）

Agent 读取以下信息完成配置：

```
📁 技能根目录: （克隆到的路径）
📁 脚本目录: scripts/mcd/
📁 数据目录: data/
📁 Token文件: data/.mcd-token

关键脚本:
  onboarding.py       - 首次引导（自动运行）
  coupon-check.py     - 每日领券（cron调用）
  expiring-points.py  - 临期积分检查（cron调用）
  surprise-alert.py   - 今日活动（点餐前调用）
  smart-combo.py      - 方案推荐（满5单后调用）
  save-order.py       - 记录订单（下单后调用）
  analyze-history.py  - 偏好分析（满5单后调用）
  calorie-tracker.py  - 热量追踪（可选）
  update-prefs.py     - 偏好管理（手动）
  track-order.py      - 订单追踪（手动）
  monthly-report.py   - 月度报告（cron调用）

配置文件（需要用户填入）:
  data/.mcd-token     - 用户的麦当劳 Token

数据文件（脚本自动生成）:
  data/mcd-preferences.json  - 用户偏好档案
  data/mcd-orders.md         - 历史订单记录
  data/mcd-calories.md       - 热量记录
```

**Agent 标准流程（每次用户说"点麦当劳"）**：

```
1. 运行 scripts/mcd/surprise-alert.py
   → 展示今日惊喜活动

2. 检查 data/mcd-orders.md 订单数量
   → <5单：直接问"你想吃什么？"
   → ≥5单：运行 scripts/mcd/smart-combo.py 展示3个方案

3. 用户确认方案后：
   mcporter call mcdonalds.calculate-price ...
   mcporter call mcdonalds.create-order ...

4. 用户报订单号后：
   - 运行 scripts/mcd/track-order.py 追踪状态
   - 运行 scripts/mcd/save-order.py '<订单JSON>' 记录订单
   - 如果订单数达到5，运行 scripts/mcd/analyze-history.py 更新偏好
```

---

## 📁 目录结构

```
mcd-skill/
├── README.md                    ← 本文件（Agent 必读）
├── SKILL.md                     ← Skill 定义文档
├── scripts/mcd/
│   ├── config.py               ← 路径配置（自动检测框架）
│   ├── mcp.py                  ← MCP 调用封装
│   ├── onboarding.py           ← 首次引导（npm install 后运行）
│   ├── coupon-check.py         ← 每日领券 cron
│   ├── expiring-points.py      ← 临期积分 cron
│   ├── surprise-alert.py        ← 今日活动
│   ├── smart-combo.py           ← 推荐方案
│   ├── save-order.py           ← 记录订单
│   ├── analyze-history.py       ← 偏好分析
│   ├── calorie-tracker.py      ← 热量追踪
│   ├── update-prefs.py          ← 偏好管理
│   ├── track-order.py           ← 订单追踪
│   └── monthly-report.py        ← 月度报告
├── data/                       ← 用户数据（token/偏好/订单）
│   └── .gitkeep
├── docs/
│   ├── MCP_API.md              ← MCP API 参考
│   └── USER_GUIDE.md           ← 用户使用指南
└── .env.example                ← 环境变量模板
```

---

## ⏰ Cron 任务（可选注册）

| 任务 | 时间 | 作用 |
|:---|:---|:---|
| coupon-check | 每天 09:00 | 自动领取优惠券 |
| expiring-points auto-redeem | 每天 10:00 | 最后一天自动兑换积分 |
| monthly-report | 每月 25 号 10:00 | 月度消费报告 |

在 OpenClaw 中注册示例：
```json
{
  "id": "mcd-coupon-check",
  "schedule": { "expr": "0 9 * * *", "tz": "Asia/Shanghai" },
  "payload": { "text": "exec:python3 /path/to/mcd-skill/scripts/mcd/coupon-check.py" }
}
```

---

## 🔧 框架适配说明

脚本会自动检测运行环境：

| 环境变量 | 框架 |
|:---|:---|
| `OPENCLAW_WORKSPACE` | OpenClaw |
| `CLAUDE_CODE_DIR` | Claude Code |
| `AGENTS_WORKSPACE` | Agents |
| `WORKSPACE` | 通用 |

若均未设置，默认使用脚本所在目录的父目录。

---

## ⚠️ 注意事项

1. **Token 有效期**：麦当劳 Token 有时效，若脚本报错401，重新获取 Token 并更新 `data/.mcd-token`
2. **积分清零**：每月最后一天会自动兑换，请确保当天 Token 有效
3. **隐私**：所有数据存储在本地 `data/` 目录，不会上传
4. **订单记录**：每次下单后建议调用 `save-order.py` 记录，历史满5单后解锁偏好功能

---

## 📄 License

MIT. 麦当劳是麦当劳公司的注册商标。本项目与麦当劳公司无关。
