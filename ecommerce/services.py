import json
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional
from uuid import uuid4

import aioredis
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.settings import settings
from ecommerce.models import Customer, Order, OrderItem, Product


CATEGORIES = ["手机数码", "家居生活", "美妆个护", "运动户外", "食品饮料", "服饰鞋包"]
STATUSES = ["paid", "shipped", "refunded", "cancelled"]
CHANNELS = ["小程序", "App", "直播间", "官网", "门店"]
CITIES = ["上海", "北京", "深圳", "广州", "杭州", "成都", "武汉", "南京", "苏州", "重庆"]
SEGMENTS = ["新客", "普通会员", "高价值会员", "企业客户"]
EVENTS_KEY = "ecommerce:events"


def seed_ecommerce_data(db: Session) -> None:
    """初始化演示数据。

    如果商品表已经有数据，就认为初始化完成，避免每次启动都重复插入。
    """

    if db.query(Product).count() > 0:
        return

    # 固定随机种子，让每次生成的数据一致，便于学习和对照。
    random.seed(20260526)

    # 生成客户数据：320 个客户，分布在不同城市和会员层级。
    customers = [
        Customer(
            id=uuid4(),
            name=f"客户{i:03d}",
            email=f"customer{i:03d}@demo.shop",
            city=random.choice(CITIES),
            segment=random.choice(SEGMENTS),
        )
        for i in range(1, 321)
    ]

    # 生成商品数据：150 个商品，平均分布在 6 个品类中。
    products = []
    for i in range(1, 151):
        category = CATEGORIES[(i - 1) % len(CATEGORIES)]
        products.append(
            Product(
                id=uuid4(),
                sku=f"SKU-{i:04d}",
                name=f"{category}商品{i:03d}",
                category=category,
                price=Decimal(random.randint(1900, 89900)) / Decimal("100"),
                stock=random.randint(20, 1200),
            )
        )

    db.add_all(customers + products)
    db.commit()

    start = datetime(2026, 1, 1, 8, 0, 0)
    orders = []
    items = []
    # 生成订单和订单明细。
    # 订单主表保存“谁在什么时候下单”；明细表保存“买了哪些商品、数量、价格”。
    for i in range(1, 2501):
        order = Order(
            id=uuid4(),
            customer_id=random.choice(customers).id,
            order_no=f"EC{2026}{i:06d}",
            status=random.choices(STATUSES, weights=[52, 34, 8, 6])[0],
            channel=random.choice(CHANNELS),
            ordered_at=start + timedelta(hours=random.randint(0, 24 * 146), minutes=random.randint(0, 59)),
        )
        orders.append(order)

        for product in random.sample(products, random.randint(1, 4)):
            quantity = random.randint(1, 5)
            discount = Decimal(random.choice([100, 100, 95, 90, 85])) / Decimal("100")
            items.append(
                OrderItem(
                    id=uuid4(),
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=(product.price * discount).quantize(Decimal("0.01")),
                )
            )

    db.add_all(orders)
    db.add_all(items)
    db.commit()


def _parse_date(value: Optional[str], fallback: datetime) -> datetime:
    if not value:
        return fallback
    return datetime.strptime(value, "%Y-%m-%d")


def _filters(start_date: Optional[str], end_date: Optional[str], category: Optional[str], status: Optional[str]):
    start = _parse_date(start_date, datetime(2026, 1, 1))
    end = _parse_date(end_date, datetime(2026, 5, 26)) + timedelta(days=1)
    conditions = [Order.ordered_at >= start, Order.ordered_at < end]
    if status:
        conditions.append(Order.status == status)
    if category:
        conditions.append(Product.category == category)
    return and_(*conditions)


def _cache_key(start_date: Optional[str], end_date: Optional[str], category: Optional[str], status: Optional[str]) -> str:
    """根据筛选条件生成 Redis key。

    同样的筛选条件会生成同样的 key，所以第二次查询可以命中缓存。
    """

    payload = {
        "start_date": start_date or "",
        "end_date": end_date or "",
        "category": category or "",
        "status": status or "",
    }
    return "ecommerce:dashboard:" + json.dumps(payload, sort_keys=True, ensure_ascii=False)


async def _redis():
    """创建 Redis 连接。

    decode_responses=True 表示 Redis 返回字符串，而不是 bytes。
    """

    return aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        decode_responses=True,
    )


def _money(value) -> float:
    return round(float(value or 0), 2)


def query_dashboard_from_postgres(
    db: Session,
    start_date: Optional[str],
    end_date: Optional[str],
    category: Optional[str],
    status: Optional[str],
) -> Dict:
    """从 PostgreSQL 聚合查询电商看板数据。"""

    conditions = _filters(start_date, end_date, category, status)
    # amount_expr 是每条订单明细的金额：数量 * 单价。
    amount_expr = OrderItem.quantity * OrderItem.unit_price

    # 第一段查询：聚合看板顶部指标。
    base = (
        db.query(
            func.count(func.distinct(Order.id)).label("orders"),
            func.count(func.distinct(Order.customer_id)).label("customers"),
            func.coalesce(func.sum(amount_expr), 0).label("revenue"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("items"),
        )
        .join(OrderItem, Order.id == OrderItem.order_id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(conditions)
        .one()
    )

    # 第二段查询：统计热销商品排行。
    top_products_rows = (
        db.query(
            Product.name,
            Product.category,
            func.sum(OrderItem.quantity).label("quantity"),
            func.sum(amount_expr).label("revenue"),
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(conditions)
        .group_by(Product.id, Product.name, Product.category)
        .order_by(func.sum(amount_expr).desc())
        .limit(8)
        .all()
    )

    # 第三段查询：查询最近订单，并聚合每笔订单金额。
    recent_rows = (
        db.query(
            Order.order_no,
            Customer.name.label("customer"),
            Order.status,
            Order.channel,
            Order.ordered_at,
            func.sum(amount_expr).label("amount"),
        )
        .join(Customer, Customer.id == Order.customer_id)
        .join(OrderItem, Order.id == OrderItem.order_id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(conditions)
        .group_by(Order.id, Order.order_no, Customer.name, Order.status, Order.channel, Order.ordered_at)
        .order_by(Order.ordered_at.desc())
        .limit(12)
        .all()
    )

    order_count = int(base.orders or 0)
    revenue = _money(base.revenue)
    avg_order = _money(revenue / order_count) if order_count else 0

    return {
        "cache": "MISS",
        "metrics": [
            {"title": "成交额", "value": revenue, "suffix": "¥"},
            {"title": "订单数", "value": order_count, "suffix": ""},
            {"title": "购买客户", "value": int(base.customers or 0), "suffix": ""},
            {"title": "客单价", "value": avg_order, "suffix": "¥"},
        ],
        "top_products": [
            {
                "name": row.name,
                "category": row.category,
                "quantity": int(row.quantity or 0),
                "revenue": _money(row.revenue),
            }
            for row in top_products_rows
        ],
        "recent_orders": [
            {
                "order_no": row.order_no,
                "customer": row.customer,
                "status": row.status,
                "channel": row.channel,
                "ordered_at": row.ordered_at.strftime("%Y-%m-%d %H:%M"),
                "amount": _money(row.amount),
            }
            for row in recent_rows
        ],
    }


async def get_dashboard_data(
    db: Session,
    start_date: Optional[str],
    end_date: Optional[str],
    category: Optional[str],
    status: Optional[str],
) -> Dict:
    """优先从 Redis 读缓存，缓存没有命中时再查 PostgreSQL。"""

    started = time.perf_counter()
    key = _cache_key(start_date, end_date, category, status)
    try:
        redis = await _redis()
        # 第一步：先去 Redis 查有没有缓存。
        cached = await redis.get(key)
        if cached:
            # 缓存命中：不查 PostgreSQL，直接返回缓存内容。
            data = json.loads(cached)
            data["cache"] = "HIT"
            data["cache_key"] = key
            data["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
            await _record_event(redis, "HIT", key, data["elapsed_ms"], "Redis")
            await redis.close()
            return data
    except Exception:
        redis = None

    # 缓存未命中：回源查询 PostgreSQL。
    data = query_dashboard_from_postgres(db, start_date, end_date, category, status)
    data["cache_key"] = key

    try:
        if redis is None:
            redis = await _redis()
        # SET key value EX 60：写入 Redis，60 秒后自动过期。
        await redis.set(key, json.dumps(data, ensure_ascii=False), ex=60)
        await redis.close()
    except Exception:
        pass

    data["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
    try:
        redis = await _redis()
        await _record_event(redis, "MISS", key, data["elapsed_ms"], "PostgreSQL -> Redis")
        await redis.close()
    except Exception:
        pass
    return data


async def clear_dashboard_cache() -> int:
    """清理本模块写入 Redis 的缓存 key。"""

    redis = await _redis()
    # keys 在生产大 Redis 中要谨慎使用；学习项目里数据很少，可以直观看效果。
    keys = await redis.keys("ecommerce:dashboard:*")
    if keys:
        await redis.delete(*keys)
    await redis.close()
    return len(keys)


async def _record_event(redis, cache: str, key: str, elapsed_ms: float, source: str) -> None:
    """把最近查询事件写入 Redis list。

    lpush 把新事件放到列表头部；ltrim 保留最近 30 条。
    """

    event = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "cache": cache,
        "source": source,
        "elapsed_ms": elapsed_ms,
        "cache_key": key,
    }
    await redis.lpush(EVENTS_KEY, json.dumps(event, ensure_ascii=False))
    await redis.ltrim(EVENTS_KEY, 0, 29)


def get_database_overview(db: Session) -> Dict:
    """返回 PostgreSQL 中的电商表概览。"""

    amount_expr = OrderItem.quantity * OrderItem.unit_price
    # group_by 订单状态，得到 paid / shipped / refunded / cancelled 的数量分布。
    status_rows = (
        db.query(Order.status, func.count(Order.id).label("count"))
        .group_by(Order.status)
        .order_by(func.count(Order.id).desc())
        .all()
    )
    # group_by 商品品类，得到每个品类的商品数和成交额。
    category_rows = (
        db.query(
            Product.category,
            func.count(func.distinct(Product.id)).label("products"),
            func.coalesce(func.sum(amount_expr), 0).label("revenue"),
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .group_by(Product.category)
        .order_by(func.sum(amount_expr).desc())
        .all()
    )
    return {
        "tables": [
            {"name": "ecommerce_customers", "rows": db.query(Customer).count(), "description": "客户表"},
            {"name": "ecommerce_products", "rows": db.query(Product).count(), "description": "商品表"},
            {"name": "ecommerce_orders", "rows": db.query(Order).count(), "description": "订单表"},
            {"name": "ecommerce_order_items", "rows": db.query(OrderItem).count(), "description": "订单明细表"},
        ],
        "status_distribution": [{"status": row.status, "count": int(row.count)} for row in status_rows],
        "category_revenue": [
            {
                "category": row.category,
                "products": int(row.products),
                "revenue": _money(row.revenue),
            }
            for row in category_rows
        ],
    }


async def get_redis_overview() -> Dict:
    """返回 Redis 缓存状态，便于观察 key、TTL 和缓存命中流程。"""

    redis = await _redis()
    # 只看本项目看板缓存 key，不扫描其他业务 key。
    keys = await redis.keys("ecommerce:dashboard:*")
    key_rows = []
    for key in sorted(keys):
        # TTL 表示 key 还有多少秒过期。
        ttl = await redis.ttl(key)
        value = await redis.get(key)
        key_rows.append(
            {
                "key": key,
                "ttl": ttl,
                "bytes": len(value or ""),
                "preview": (value or "")[:160],
            }
        )
    info = await redis.info("memory")
    await redis.close()
    return {
        "key_count": len(keys),
        "keys": key_rows,
        "memory": {
            "used_memory_human": info.get("used_memory_human"),
            "used_memory_peak_human": info.get("used_memory_peak_human"),
        },
        "flow": [
            "浏览器发起筛选查询",
            "FastAPI 生成 Redis cache key",
            "Redis GET key",
            "命中 HIT：直接返回缓存 JSON",
            "未命中 MISS：查询 PostgreSQL 聚合数据",
            "FastAPI SET key EX 60 写入 Redis",
            "JSON 返回前端渲染",
        ],
    }


async def get_recent_events() -> Dict:
    """返回最近的查询事件，帮助观察缓存命中变化。"""

    redis = await _redis()
    # Redis list 中保存最近 30 次查询事件。
    rows = await redis.lrange(EVENTS_KEY, 0, 29)
    await redis.close()
    return {"events": [json.loads(row) for row in rows]}
