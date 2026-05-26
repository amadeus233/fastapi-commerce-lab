from functools import reduce
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, MetaData
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from .db import metadata


@as_declarative()
class Base:
    """所有 SQLAlchemy 模型的基础类。

    业务模型继承 Base 后，会自动拥有：
    - id 主键字段
    - metadata 表结构集合
    - 默认表名规则
    """

    # __name__ 是类名，SQLAlchemy 的声明式基类需要这个类型提示。
    __name__: str

    # 每张表默认都有一个 UUID 主键。
    # Column(...) 表示数据库字段；primary_key=True 表示主键；default=uuid4 表示自动生成 UUID。
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    @declared_attr
    def metadata(cls) -> MetaData:
        # declared_attr 表示这个属性会在子类声明时动态计算。
        # 这里让所有模型共享 app.db 中的同一个 metadata。
        return metadata

    @declared_attr
    def __tablename__(cls) -> str:
        # 默认表名是类名小写。例如 class User(Base) 对应表名 user。
        return cls.__name__.lower()
