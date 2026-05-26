from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.base import Base


class Customer(Base):
    """客户表：保存电商平台里的购买用户。"""

    # 显式指定表名，避免默认表名 customer 太泛。
    __tablename__ = "ecommerce_customers"

    # 普通字符串字段。nullable=False 表示不能为空。
    name = Column(String(120), nullable=False)
    # email 加唯一约束和索引，模拟真实用户账号字段。
    email = Column(String(255), unique=True, index=True, nullable=False)
    city = Column(String(80), nullable=False)
    segment = Column(String(40), nullable=False)

    # relationship 是 SQLAlchemy ORM 关系。
    # 一个客户可以有多笔订单，Order.customer 会反向指回客户。
    orders = relationship("Order", back_populates="customer")


class Product(Base):
    """商品表：保存商品基础信息。"""

    __tablename__ = "ecommerce_products"

    # SKU 是电商系统里常见的商品编码。
    sku = Column(String(40), unique=True, index=True, nullable=False)
    name = Column(String(160), nullable=False)
    category = Column(String(80), index=True, nullable=False)
    # Numeric 适合存金额，避免 float 精度问题。
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    """订单表：一笔订单属于一个客户，可以包含多个商品明细。"""

    __tablename__ = "ecommerce_orders"

    # ForeignKey 表示外键：订单属于某个客户。
    customer_id = Column(UUID(as_uuid=True), ForeignKey("ecommerce_customers.id"), nullable=False)
    order_no = Column(String(40), unique=True, index=True, nullable=False)
    # status 建索引，方便按订单状态筛选。
    status = Column(String(30), index=True, nullable=False)
    channel = Column(String(40), nullable=False)
    # ordered_at 建索引，方便按日期范围查询。
    ordered_at = Column(DateTime, index=True, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """订单明细表：记录订单中的具体商品、数量和成交价。"""

    __tablename__ = "ecommerce_order_items"

    # 订单明细通过两个外键连接订单和商品。
    order_id = Column(UUID(as_uuid=True), ForeignKey("ecommerce_orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("ecommerce_products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
