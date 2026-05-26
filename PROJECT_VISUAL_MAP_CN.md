# fastapi-commerce-lab 可视化学习地图

## 1. 总体架构

```mermaid
flowchart TB
    Browser[浏览器电商看板] --> API[FastAPI / Uvicorn]
    API --> Router[app/routes.py]
    Router --> Ecommerce[ecommerce/api.py]
    Ecommerce --> Service[ecommerce/services.py]
    Service --> Redis[(Redis)]
    Service --> PG[(PostgreSQL)]
    PG --> Models[ecommerce/models.py]
    Redis --> Events[ecommerce:events]
    Redis --> CacheKeys[ecommerce:dashboard:*]
    Service --> Dashboard[ecommerce/dashboard.py]
```

## 2. Docker 服务图

```mermaid
flowchart LR
    Browser[localhost:11000] --> Web[web 容器<br/>FastAPI]
    Web --> PG[postgres 容器<br/>5432]
    Web --> Redis[redis 容器<br/>6379]
```

## 3. 电商数据表关系

```mermaid
erDiagram
    ecommerce_customers ||--o{ ecommerce_orders : places
    ecommerce_orders ||--o{ ecommerce_order_items : contains
    ecommerce_products ||--o{ ecommerce_order_items : appears_in

    ecommerce_customers {
      uuid id
      string name
      string email
      string city
      string segment
    }
    ecommerce_products {
      uuid id
      string sku
      string name
      string category
      numeric price
      int stock
    }
    ecommerce_orders {
      uuid id
      uuid customer_id
      string order_no
      string status
      string channel
      datetime ordered_at
    }
    ecommerce_order_items {
      uuid id
      uuid order_id
      uuid product_id
      int quantity
      numeric unit_price
    }
```

## 4. Redis HIT / MISS 流程

```mermaid
sequenceDiagram
    participant UI as 前端页面
    participant API as FastAPI
    participant R as Redis
    participant PG as PostgreSQL

    UI->>API: GET /metrics?筛选条件
    API->>API: 生成 cache key
    API->>R: GET ecommerce:dashboard:{...}
    alt HIT
        R-->>API: 返回缓存 JSON
        API-->>UI: cache=HIT
    else MISS
        R-->>API: nil
        API->>PG: 聚合查询订单/商品/客户
        PG-->>API: 返回统计结果
        API->>R: SET key value EX 60
        API-->>UI: cache=MISS
    end
    API->>R: LPUSH ecommerce:events 查询事件
```

## 5. 页面视图映射

```mermaid
flowchart TB
    Page[电商数据平台页面] --> Overview[经营总览]
    Page --> Products[商品排行]
    Page --> Orders[订单监控]
    Page --> Postgres[PostgreSQL]
    Page --> RedisView[Redis Cache]
    Page --> Logs[API Logs]

    Overview --> MetricsAPI[/GET metrics/]
    Products --> MetricsAPI
    Orders --> MetricsAPI
    Postgres --> DatabaseAPI[/GET database/]
    RedisView --> RedisAPI[/GET redis/]
    Logs --> EventsAPI[/GET events/]
```

## 6. 学习路线

```mermaid
flowchart LR
    A[main.py<br/>入口] --> B[app/routes.py<br/>路由汇总]
    B --> C[ecommerce/api.py<br/>接口]
    C --> D[ecommerce/services.py<br/>业务逻辑]
    D --> E[ecommerce/models.py<br/>表结构]
    D --> F[Redis 缓存]
    E --> G[PostgreSQL 数据]
    C --> H[ecommerce/dashboard.py<br/>前端页面]
```

## 7. 最重要的观察点

- 第一次相同筛选条件：`CACHE MISS`
- 第二次相同筛选条件：`CACHE HIT`
- `Redis Cache` 页面看 key、TTL、value 预览
- `API Logs` 页面看事件顺序
- `PostgreSQL` 页面看表数据量和聚合结果
