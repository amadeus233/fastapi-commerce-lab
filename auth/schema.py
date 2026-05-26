from app.schema import BaseSchema


class LoginSchema(BaseSchema):
    """登录接口请求体结构。

    Pydantic 会根据下面的类型注解检查请求数据：
    - email 必须是字符串
    - password 必须是字符串
    """

    email: str
    password: str
