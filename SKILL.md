---
name: mcd-skill
description: >-
  麦当劳 (McDonald's / 金拱门): order meals, browse the menu, check deals and coupons,
  manage taste preferences, track delivery, review spending and points (积分), set a budget,
  or check calories. Trigger whenever the user mentions 麦当劳, 金拱门, McDonald's, or any
  named McDonald's product (巨无霸, 麦辣鸡腿堡, etc.) — even in short commands like 点麦当劳.
  Also trigger when a user wants to order food, check promotions, or manage food preferences
  involving McDonald's. Exclude: KFC/肯德基, Burger King/汉堡王, general restaurant
  recommendations, unbranded 外卖/快餐 queries, and bank/card rewards points.
---

# McDonald's 点餐助手

A zero-configuration skill for the full McDonald's delivery experience — ordering, deals, coupons, points tracking, and taste preference learning.

---

## First-time setup

Before using any feature, the user needs a valid McDonald's token:

1. Ask the user to open the 麦当劳 App, log in, visit https://mcp.mcd.cn, scan the QR code to authorize, and copy the token.
2. Save the token: `mkdir -p data && echo "<token>" > data/.mcd-token`
3. Run the onboarding script to verify the token and initialize preferences:
   ```bash
   python3 scripts/mcd/onboarding.py
   ```

Onboarding auto-checks: token validity, account points, coupon binding, delivery addresses, and taste preferences.

If the user says they don't have a token, walk them through the steps above before doing anything else.

---

## Core ordering flow

When the user says something like "点麦当劳" or "I want McDonald's", follow this sequence:

### Step 1: Show today's surprises
Run `scripts/mcd/surprise-alert.py` to display today's deals, new items, and limited-time offers. This gives the user context on what's available before they decide.

### Step 2: Recommend or ask
Check `data/mcd-orders.md` for the number of past orders:

- **< 5 orders**: Don't try to analyze preferences — there isn't enough data. Just ask "What do you feel like eating?" and let the user browse freely.
- **≥ 5 orders**: Run `scripts/mcd/smart-combo.py` to generate 3 personalized meal plans based on their taste profile and budget. Present all three with prices and tags.

### Step 3: Calculate price and apply best coupon
Once the user picks a meal, use the MCP to calculate the price, then apply the best available coupon. Show the final price before creating the order.

Use `mcporter call mcdonalds.calculate-price` and `mcporter call mcdonalds.query-store-coupons` — see `docs/MCP_API.md` for exact parameters.

### Step 4: Create order
Use `mcporter call mcdonalds.create-order` with the confirmed items. The API returns a payment link — share it with the user so they can pay through the McDonald's app.

### Step 5: Post-order tracking
After the user shares the order number (34 digits):
1. Run `scripts/mcd/track-order.py <orderNumber>` to track delivery status
2. Run `scripts/mcd/save-order.py '<orderJSON>'` to record the order
3. If the order count reaches 5, run `scripts/mcd/analyze-history.py` to unlock preference learning

---

## Other user interactions

| User says | What to do |
|:---|:---|
| 有什么优惠 / any deals? | Run `scripts/mcd/surprise-alert.py` |
| 查积分 / check my points | Run `scripts/mcd/expiring-points.py check` |
| 我不吃辣 / I don't like spicy | Run `scripts/mcd/update-prefs.py taste spicy 1` |
| 喜欢甜的 / I prefer sweet | Run `scripts/mcd/update-prefs.py taste sweet 5` |
| 查热量 / how many calories? | Run `scripts/mcd/calorie-tracker.py report` |
| 月度报告 / monthly report | Run `scripts/mcd/monthly-report.py` |
| Track order number ... | Run `scripts/mcd/track-order.py <34-digit-order-number>` |
| 修改预算 / change budget | Edit `data/mcd-preferences.json` manually or guide the user |

---

## Key constraints

**5-order threshold for preference learning**: Don't analyze taste preferences from a single order — it's too noisy and accidental. The `smart-combo.py` and `analyze-history.py` scripts require at least 5 historical orders to produce reliable recommendations. This is hardcoded in the scripts for a reason.

**Token expiration**: McDonald's tokens expire periodically. If any MCP call returns a 401 error, tell the user their token needs refreshing and walk them through the setup steps again.

**Local data only**: All user data (preferences, order history, calories) is stored locally in the `data/` directory. Never upload or share this data.

---

## Script reference

All scripts live under `scripts/mcd/`. Each is self-contained and can be run directly:

| Script | Purpose | When to run |
|:---|:---|:---|
| `onboarding.py` | First-time setup + token verification | Once, during initial setup |
| `surprise-alert.py` | Show today's deals and events | Every time user starts an order |
| `smart-combo.py` | Generate 3 personalized meal plans | When user has ≥5 orders and wants a recommendation |
| `save-order.py` | Append order to history file | After each confirmed order |
| `analyze-history.py` | Learn taste preferences from history | After reaching the 5-order threshold |
| `calorie-tracker.py` | Show daily/weekly/monthly calorie stats | When user asks about calories |
| `expiring-points.py` | Check points, auto-redeem on last day of month | `check` for inquiry, `auto-redeem` for cron |
| `coupon-check.py` | Auto-claim available coupons | Daily cron (09:00) |
| `update-prefs.py` | Read/write taste preferences | When user wants to adjust preferences |
| `track-order.py` | Track delivery status by order number | When user provides a 34-digit order number |
| `monthly-report.py` | Generate monthly spending + points report | Monthly cron (25th at 10:00) |
| `mcp_client.py` | Shared MCP call wrapper | Imported by other scripts, not run directly |

For detailed MCP API parameters (beCode, storeCode, etc.), read `docs/MCP_API.md`.

---

## Data files

| File | Format | Purpose |
|:---|:---|:---|
| `data/.mcd-token` | Plain text | User's McDonald's API token |
| `data/mcd-preferences.json` | JSON | Taste profile, budget, favorite items |
| `data/mcd-orders.md` | Markdown | Order history (appended, not overwritten) |
| `data/mcd-calories.md` | Markdown | Calorie tracking records |

Scripts auto-create these files as needed. The `data/` directory is created on first run if it doesn't exist.

---

## Cron tasks (optional)

For fully automated operation, register these as cron/scheduled tasks in the agent framework:

| Task | Schedule | Script |
|:---|:---|:---|
| Auto-claim coupons | Daily at 09:00 CST | `scripts/mcd/coupon-check.py` |
| Points auto-redeem | Daily at 10:00 CST (acts on last day of month) | `scripts/mcd/expiring-points.py auto-redeem` |
| Monthly report | 25th of each month at 10:00 CST | `scripts/mcd/monthly-report.py` |
