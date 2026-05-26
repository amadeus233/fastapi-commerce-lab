from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class BaseSchema(BaseModel):
    """所有 Pydantic Schema 的基础类。

    Schema 通常用于描述接口请求体和响应体。
    Pydantic 会根据类型注解自动校验数据。
    """

    def to_dict(self) -> Any:
        # jsonable_encoder 会把 Pydantic 对象转换成 JSON 友好的普通 Python 对象。
        # 例如 UUID、datetime 等特殊类型会被转换成字符串。
        return jsonable_encoder(self)
