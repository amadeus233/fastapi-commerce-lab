# fastapi-commerce-lab 中文深度 Review

## 项目定位

这个项目从一个 FastAPI 模板扩展成了“电商数据平台学习项目”。它适合用来学习：

- 后端项目分层
- Docker Compose 如何编排多个服务
- PostgreSQL 如何存业务数据
- Redis 如何做应用层缓存
- 前端如何通过 API 查询后端数据
- 缓存命中 `HIT` 和未命中 `MISS` 的实际变化

## 总体架构

```text
浏览器页面
  ↓
FastAPI / Uvicorn
  ↓
路由层 app/routes.py
  ↓
业务模块 ecommerce/api.py
  ↓
业务逻辑 ecommerce/services.py
  ↓
Redis / PostgreSQL
```

## 目录职责

| 路径 | 职责 |
| --- | --- |
| `main.py` | 应用入口，挂载路由，启动时连接数据库并初始化电商数据 |
| `app/settings.py` | 读取 `.env` 配置 |
| `app/db.py` | 创建数据库连接、engine、session |
| `app/base.py` | SQLAlchemy 模型基类 |
| `app/routes.py` | 总路由汇总 |
| `app/models.py` | 模型汇总，供建表和 Alembic 发现 |
| `auth/` | 原始认证模块示例 |
| `ecommerce/` | 电商数据平台核心模块 |
| `alembic/` | 数据库迁移配置 |
| `visuals/` | 图片版可视化说明 |

## ecommerce 模块

| 文件 | 作用 |
| --- | --- |
| `ecommerce/models.py` | 定义客户、商品、订单、订单明细 4 张表 |
| `ecommerce/services.py` | 生成演示数据、查询 PostgreSQL、读写 Redis、记录事件 |
| `ecommerce/api.py` | 提供页面和 API 接口 |
| `ecommerce/dashboard.py` | 原生 HTML/CSS/JS 前端页面 |
| `ecommerce/schema.py` | 响应结构示例 |

## 数据库设计

当前有 4 张电商表：

| 表 | 说明 |
| --- | --- |
| `ecommerce_customers` | 客户 |
| `ecommerce_products` | 商品 |
| `ecommerce_orders` | 订单主表 |
| `ecommerce_order_items` | 订单明细 |

关系：

```text
Customer 1 -> N Order
Order    1 -> N OrderItem
Product  1 -> N OrderItem
```

## Redis 用法

当前 Redis 用了两类数据：

| Key | 类型 | 作用 |
| --- | --- | --- |
| `ecommerce:dashboard:{筛选条件}` | String | 缓存看板查询结果 |
| `ecommerce:events` | List | 记录最近查询事件 |

看板缓存默认 60 秒过期：

```text
Redis SET key value EX 60
```

## 请求链路

第一次查询：

```text
前端点击查询
  ↓
GET /api/v1/ecommerce/metrics
  ↓
Redis GET key
  ↓
MISS
  ↓
PostgreSQL 聚合查询
  ↓
Redis SET key EX 60
  ↓
返回 JSON 给前端
```

第二次相同查询：

```text
前端点击查询
  ↓
GET /api/v1/ecommerce/metrics
  ↓
Redis GET key
  ↓
HIT
  ↓
直接返回缓存 JSON
```

## 页面视图

| 菜单 | 学习点 |
| --- | --- |
| 经营总览 | API 查询、指标聚合、缓存 HIT/MISS |
| 商品排行 | PostgreSQL group by 商品 |
| 订单监控 | 订单明细展示 |
| PostgreSQL | 表数据量、状态分布、品类成交额 |
| Redis Cache | key、TTL、内存、缓存流程 |
| API Logs | 最近事件，观察 MISS 到 HIT |

## 当前优点

- 保留了原项目的模块分层
- PostgreSQL 和 Redis 都真实参与链路
- 有可视化页面，适合初学者观察
- Docker Compose 一键启动
- 源码有大量中文注释

## 当前限制

- 数据是模拟数据，不是真实电商交易
- 没有用户登录和权限控制
- 没有正式 Alembic 迁移脚本
- `DEBUG` 配置仍沿用模板写法，生产环境需修正
- 前端是原生 HTML，不是 React/Vue 工程

## 适合继续练习的方向

1. 增加用户登录
2. 增加商品搜索和分页
3. 增加订单详情页
4. 改用 Alembic 管理表结构
5. 给 Redis 缓存增加主动失效策略
6. 把前端拆成独立 Vue/React 项目
