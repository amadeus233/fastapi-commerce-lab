# 电商数据平台学习说明

## 页面入口

```text
http://localhost:11000/api/v1/ecommerce/dashboard
```

## 当前功能

- 经营总览
- 商品排行
- 订单监控
- PostgreSQL 数据可视化
- Redis Cache 可视化
- API Logs 查询事件
- Swagger API 文档

## 数据来源说明

数据是项目生成的模拟电商数据，不是真实生产数据。

但技术链路是真实的：

```text
前端页面
  -> FastAPI
  -> Redis
  -> PostgreSQL
  -> Redis
  -> 前端渲染
```

## 数据库表

| 表名 | 说明 | 数据量 |
| --- | --- | --- |
| `ecommerce_customers` | 客户表 | 320 |
| `ecommerce_products` | 商品表 | 150 |
| `ecommerce_orders` | 订单主表 | 2500 |
| `ecommerce_order_items` | 订单明细表 | 6264 |

## Redis 缓存

看板缓存 key：

```text
ecommerce:dashboard:{筛选条件}
```

事件日志 key：

```text
ecommerce:events
```

第一次查询：

```text
MISS -> 查 PostgreSQL -> 写 Redis
```

第二次相同查询：

```text
HIT -> 直接读 Redis
```

## API

| 接口 | 作用 |
| --- | --- |
| `GET /api/v1/ecommerce/dashboard` | 页面 |
| `GET /api/v1/ecommerce/metrics` | 看板数据 |
| `GET /api/v1/ecommerce/database` | PostgreSQL 概览 |
| `GET /api/v1/ecommerce/redis` | Redis 概览 |
| `GET /api/v1/ecommerce/events` | 查询事件 |
| `POST /api/v1/ecommerce/seed` | 初始化演示数据 |
| `DELETE /api/v1/ecommerce/cache` | 清理看板缓存 |

## 学 Redis 的操作步骤

1. 打开页面。
2. 点“查询数据”。
3. 看顶部 `CACHE MISS`。
4. 再点一次相同条件。
5. 看顶部变成 `CACHE HIT`。
6. 切到 `Redis Cache` 看 key 和 TTL。
7. 切到 `API Logs` 看最近事件。

## 常用命令

查看 Redis key：

```powershell
docker-compose exec redis redis-cli keys "ecommerce:*"
```

查看 Redis list：

```powershell
docker-compose exec redis redis-cli lrange ecommerce:events 0 10
```

查看 PostgreSQL 表数据量：

```powershell
docker-compose exec postgres psql -U sasori -d akatsuki -c "select 'customers' as table, count(*) from ecommerce_customers union all select 'products', count(*) from ecommerce_products union all select 'orders', count(*) from ecommerce_orders union all select 'order_items', count(*) from ecommerce_order_items;"
```
