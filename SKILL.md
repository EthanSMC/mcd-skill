# McDonald's 点餐助手 Skill

*装上就能用，零配置完成麦当劳外卖完全场景*

---

## 🚀 首次安装

**Step 1：** 配置 Token
```bash
mkdir -p data && echo "你的Token" > data/.mcd-token
```

**Step 2：** 运行引导
```bash
python3 scripts/mcd/onboarding.py
```

**Step 3：** 开始使用 — 对 Agent 说「点麦当劳」

---

## 🍔 完整点餐流程

```
用户：「点麦当劳」
Agent：
  1. scripts/mcd/surprise-alert.py → 展示今日惊喜
  2. 检查历史订单数 < 5？
       ├─ 是 → 直接问「你想吃什么」
       └─ 否 → scripts/mcd/smart-combo.py → 展示3个方案

用户：选了方案
Agent：
  mcporter call mcdonalds.calculate-price ...
  → 展示价格 + 最优券 → 用户确认

用户：确认
Agent：
  mcporter call mcdonalds.create-order ...
  → 返回支付链接

用户：支付完成，订单号 1030938730000733964700499858
Agent：
  scripts/mcd/track-order.py → 追踪状态
  scripts/mcd/save-order.py → 记录订单
  （满5单）scripts/mcd/analyze-history.py → 更新偏好
```

---

## 🔐 偏好解锁规则

| 历史订单 | 解锁状态 |
|:---:|:---|
| 0-4 笔 | ❌ 不解锁，用默认值（辣3/咸4/甜3） |
| ≥5 笔 | ✅ 解锁 Smart Combo + 口味推荐 |

**为什么5笔？** 历史统计比单次数据可靠，避免偶然性干扰。

---

## 📁 数据文件

| 文件 | 作用 |
|:---|:---|
| `data/.mcd-token` | 用户麦当劳 Token |
| `data/mcd-preferences.json` | 偏好档案 |
| `data/mcd-orders.md` | 历史订单（追加） |
| `data/mcd-calories.md` | 热量记录 |

---

## 🛠️ 脚本清单

| 脚本 | 作用 | 触发 |
|:---|:---|:---|
| `onboarding.py` | 首次引导+Token验证 | 首次运行 |
| `surprise-alert.py` | 今日惊喜活动 | 点餐时 |
| `smart-combo.py` | 3个推荐方案 | ≥5单点餐时 |
| `save-order.py` | 记录订单到md | 下单确认后 |
| `analyze-history.py` | 从历史学习口味 | ≥5单新订单后 |
| `calorie-tracker.py` | 热量追踪报告 | 用户查热量时 |
| `expiring-points.py` | 临期积分检查+自动兑换 | 每天cron |
| `coupon-check.py` | 自动领取优惠券 | 每天cron |
| `update-prefs.py` | 偏好增删改查 | 用户修改时 |
| `track-order.py` | 订单追踪 | 用户报订单号时 |
| `mcp_client.py` | MCP 调用封装 | 所有脚本共用 |
| `monthly-report.py` | 月度消费报告 | 每月cron |

---

## 🎁 临期积分自动兑换逻辑

```
每天 10:00 检查：
  今天是本月最后一天？
    ├─ 否 → 跳过
    └─ 是 → 自动兑换性价比最高的可兑方案
              → 调用 mall-create-order
              → 通知用户兑换结果
```

---

## 🔑 Token 配置

Token 文件路径：`data/.mcd-token`

获取方式：
1. 麦当劳 App 登录
2. mcp.mcd.cn 官网扫码授权
3. 复制 Token 写入 `data/.mcd-token`

---

## ⚠️ 重要约束

- **不**从单次订单直接记录口味偏好（偶然性太大）
- **必须**积累满5单历史才解锁偏好模块
- **Token** 有时效，若报401请重新获取
