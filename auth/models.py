from typing import Type

from sqlalchemy import Column, String

from app.base import Base


class User(Base):
    """用户数据库模型。

    这个类继承 app.base.Base，所以自动拥有 id 主键字段。
    当前模板只定义了 email 字段，还没有 password_hash 等真实登录所需字段。
    """

    # Column 表示数据库字段。
    # String(255) 表示最多 255 字符。
    # unique=True 表示邮箱不能重复。
    # index=True 表示给邮箱建索引，查询更快。
    # nullable=False 表示不能为空。
    email = Column(String(255), unique=True, index=True, nullable=False)

    @classmethod
    def to_dict(cls, instance: Type[Base]):
        """把 SQLAlchemy 模型实例转换成普通字典。

        @classmethod 表示这是类方法，第一个参数 cls 是类本身，不是实例 self。
        instance 是要转换的模型对象。
        """

        result = {}

        # instance.__table__.columns 可以遍历这个模型对应表的所有字段。
        for column in instance.__table__.columns:
            # getattr(instance, column.name) 按字段名动态读取实例上的值。
            # str(...) 把 UUID 等类型统一转成字符串，方便 JSON 返回。
            result[column.name] = str(getattr(instance, column.name))

        return result
