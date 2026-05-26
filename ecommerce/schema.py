from typing import List

from pydantic import BaseModel


class MetricCard(BaseModel):
    """顶部指标卡片结构。"""

    title: str
    value: float
    suffix: str = ""


class TopProduct(BaseModel):
    """热销商品排行结构。"""

    name: str
    category: str
    quantity: int
    revenue: float


class RecentOrder(BaseModel):
    """最近订单结构。"""

    order_no: str
    customer: str
    status: str
    channel: str
    ordered_at: str
    amount: float


class DashboardPayload(BaseModel):
    """电商看板整体响应结构。

    当前接口直接返回 dict，这个 schema 主要用于学习响应数据应该如何建模。
    """

    cache: str
    metrics: List[MetricCard]
    top_products: List[TopProduct]
    recent_orders: List[RecentOrder]
