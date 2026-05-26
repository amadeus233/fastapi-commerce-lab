from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from ecommerce.dashboard import DASHBOARD_HTML
from ecommerce.services import (
    clear_dashboard_cache,
    get_dashboard_data,
    get_database_overview,
    get_recent_events,
    get_redis_overview,
    seed_ecommerce_data,
)


# 这个 router 是电商模块自己的路由集合。
# prefix="/ecommerce" 表示这个模块的接口都会以 /ecommerce 开头。
# main.py 又把总路由挂到了 /api/v1，所以最终路径是 /api/v1/ecommerce/...
router = APIRouter(prefix="/ecommerce", tags=["ecommerce"])


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page() -> HTMLResponse:
    """电商数据平台页面。"""

    # 这里返回的是一整段 HTML 字符串。
    # 这样做是为了学习方便：不用额外引入 React/Vue，也能看到一个前端界面。
    return HTMLResponse(DASHBOARD_HTML)


@router.get("/metrics")
async def metrics(
    start_date: Optional[str] = Query(None, description="开始日期，格式 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式 YYYY-MM-DD"),
    category: Optional[str] = Query(None, description="商品品类"),
    status: Optional[str] = Query(None, description="订单状态"),
    db: Session = Depends(get_db),
):
    """返回电商看板数据。

    第一次查询会访问 PostgreSQL 并写入 Redis。
    相同筛选条件 60 秒内再次查询，会直接命中 Redis。
    """

    # Query(...) 用于声明 URL 查询参数。
    # Depends(get_db) 是 FastAPI 依赖注入：每次请求自动给接口函数传入数据库 session。
    return await get_dashboard_data(db, start_date, end_date, category, status)


@router.post("/seed")
async def seed(db: Session = Depends(get_db)):
    """手动初始化演示数据。启动时也会自动执行一次。"""

    # 这个接口适合你手动补数据。
    # seed_ecommerce_data 内部会先检查是否已有商品数据，避免重复灌入。
    seed_ecommerce_data(db)
    deleted = await clear_dashboard_cache()
    return {"message": "seed completed", "cleared_cache_keys": deleted}


@router.delete("/cache")
async def clear_cache():
    """清理电商看板 Redis 缓存。"""

    # 删除 ecommerce:dashboard:* 这类 key，让下一次查询重新走 PostgreSQL。
    deleted = await clear_dashboard_cache()
    return {"deleted": deleted}


@router.get("/database")
async def database_overview(db: Session = Depends(get_db)):
    """查看 PostgreSQL 电商数据概览。"""

    # 返回表数据量、订单状态分布、品类成交额。
    return get_database_overview(db)


@router.get("/redis")
async def redis_overview():
    """查看 Redis 缓存 key、TTL 和内存情况。"""

    # 返回 Redis key 列表、TTL、value 预览、内存信息和缓存流程说明。
    return await get_redis_overview()


@router.get("/events")
async def events():
    """查看最近查询事件，观察缓存 MISS/HIT。"""

    # 事件日志也存放在 Redis list 中，便于学习 Redis 不只是 key-value。
    return await get_recent_events()
