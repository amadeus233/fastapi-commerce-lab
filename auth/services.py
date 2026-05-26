from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.services import BaseService
from app.settings import settings

# OAuth2PasswordBearer 是 FastAPI 提供的安全认证工具。
# 它会让 Swagger 文档里出现 Authorize 按钮，方便你在 /docs 页面测试带 token 的接口。
reuseable_oauth = OAuth2PasswordBearer(
    # tokenUrl 是获取 token 的接口地址。
    # 注意：当前模板还没有实现 /api/v1/user/login，所以这里是一个待补全点。
    tokenUrl="/api/v1/user/login",
    scheme_name="JWT"
)


def hash_password(password: str) -> str:
    """把明文密码转换成哈希密码。

    语法解析：
    - password: str 是类型注解，表示参数应该是字符串。
    - -> str 表示函数返回字符串。
    """

    # 永远不要把用户明文密码直接存进数据库。
    # hash(...) 会生成不可逆的密码哈希值。
    hashed_password = settings.PASSWORD_HASHER.hash(password)
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码是否匹配数据库中的哈希密码。"""

    # verify 会把用户输入的明文密码按同样规则处理，再和已有哈希值比较。
    password_is_verified = settings.PASSWORD_HASHER.verify(
        plain_password, hashed_password
    )

    # bool(...) 确保返回值一定是 True 或 False。
    return bool(password_is_verified)


def create_auth_token(payload: Dict[str, Any], expiry: int) -> str:
    """创建 JWT 认证 token。

    参数说明：
    - payload：要写进 token 的业务数据，例如用户 id、邮箱等。
    - expiry：过期时间，单位是秒。
    """

    # datetime.now() 获取当前时间；timedelta(seconds=expiry) 表示一段时间差。
    # 二者相加得到 token 的过期时间。
    expiry_delta = datetime.now() + timedelta(seconds=expiry)

    # data_to_encode 是最终要写进 JWT 的内容。
    # data 放业务数据，expiry 放过期时间。
    data_to_encode = {"expiry": str(expiry_delta), "data": payload}

    # jwt.encode 会把字典编码成一个签名字符串。
    # SECRET_KEY 用来签名，JWT_ALGORITHM 指定签名算法。
    encoded_data: str = jwt.encode(
        data_to_encode, settings.SECRET_KEY, settings.JWT_ALGORITHM
    )

    return encoded_data


class UserService(BaseService):
    """用户业务服务类。

    这里继承 BaseService，所以可以使用 self.db 和 self.save(...)。
    当前类还只是模板占位，没有实现真正注册、登录、查询用户等业务。
    """

    def a_method(self):
        """演示如何使用 self.save 的占位方法。

        真实项目中应该删除这个方法，换成 create_user、login_user 等明确业务方法。
        """

        # ... 是 Python 的 Ellipsis 对象，这里只是占位，不是真正可保存的模型。
        model_instance = ...
        # self.save 继承自 BaseService，会执行 add、commit、refresh。
        self.save(model_instance)
