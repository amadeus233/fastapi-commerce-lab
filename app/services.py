from typing import Type

from sqlalchemy.orm import Session

from .base import Base


class BaseService:
    """业务服务层基类。

    Service 层通常放“业务逻辑”，比如注册用户、创建订单、查询列表。
    这个基类把数据库 session 保存到 self.db，并提供一个通用 save 方法。
    """

    def __init__(self, db: Session) -> None:
        # __init__ 是构造函数。创建 Service 对象时，需要传入一个数据库 Session。
        self.db = db

    def save(self, model: Type[Base]) -> None:
        # add：把模型对象加入当前数据库会话。
        self.db.add(model)
        # commit：提交事务，真正写入数据库。
        self.db.commit()
        # refresh：重新从数据库读取对象，拿到数据库生成的默认值。
        self.db.refresh(model)
