# McDonald's MCP API 参考

*通过 mcporter 调用，格式：`mcporter call mcdonalds.<method> key=value ...`*

---

## 账户

### query-my-account
查询账户积分/状态
```
mcporter call mcdonalds.query-my-account
```
返回：`availablePoint`, `currentMouthExpirePoint`, `accumulativePoint`, `accountId`

---

## 优惠券

### auto-bind-coupons
自动领取所有可领券
```
mcporter call mcdonalds.auto-bind-coupons
```

### query-my-coupons
查询已领取的券
```
mcporter call mcdonalds.query-my-coupons
```

### query-store-coupons
查询指定门店可用券
```
mcporter call mcdonalds.query-store-coupons beCode="145058702" storeCode="1450587" orderType="2"
```

### available-coupons
查询可领取券
```
mcporter call mcdonalds.available-coupons
```

---

## 门店

### query-nearby-stores
搜索附近门店
```
mcporter call mcdonalds.query-nearby-stores beType="2" searchType="2" city="上海" keyword="张杨路"
```

### delivery-query-addresses
查询配送地址
```
mcporter call mcdonalds.delivery-query-addresses beType="2"
```

---

## 餐品

### query-meals
查询餐品列表
```
mcporter call mcdonalds.query-meals beCode="145058702" orderType="2" storeCode="1450587"
```

### query-meal-detail
查餐品详情
```
mcporter call mcdonalds.query-meal-detail beCode="145058702" code="9900003007" orderType="2" storeCode="1450587"
```

### list-nutrition-foods
查营养信息
```
mcporter call mcdonalds.list-nutrition-foods productCodes='["9900003007"]'
```

---

## 下单

### calculate-price
计算价格
```
mcporter call mcdonalds.calculate-price \
  beCode="145058702" \
  items='[{"productCode":"9900003007","quantity":1}]' \
  orderType="2" \
  storeCode="1450587"
```

### create-order
创建订单
```
mcporter call mcdonalds.create-order \
  addressId="配送地址ID" \
  beCode="145058702" \
  items='[{"productCode":"9900003007","quantity":1}]' \
  orderType="2" \
  storeCode="1450587"
```

### query-order
查询订单状态
```
mcporter call mcdonalds.query-order orderId="34位订单号"
```

---

## 积分商城

### mall-points-products
查询积分商品
```
mcporter call mcdonalds.mall-points-products pageSize=20
```

### mall-create-order
积分兑换
```
mcporter call mcdonalds.mall-create-order skuId="16555" spuId="15865" shopId=2 points=50
```

---

## 活动

### campaign-calendar
查询活动日历（今日活动）
```
mcporter call mcdonalds.campaign-calendar
```

---

## 常用参数

| 参数 | 值 | 说明 |
|:---|:---:|:---|
| `beType` | `1`=到店 / `2`=外送 | 场景类型 |
| `orderType` | `2`=外送 | 订单类型 |
| `storeCode` | 门店编码 | 如 `1450587` |
| `beCode` | 门店编码+02 | 如 `145058702` |
