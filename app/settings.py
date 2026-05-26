from os import environ

from passlib.context import CryptContext


class Settings:
    """集中管理项目配置。

    这个类会从环境变量读取配置。Docker Compose 启动时会把 .env 文件里的内容
    注入为环境变量，所以这里可以通过 environ.get(...) 读取。
    """

    # 应用标题，会显示在 FastAPI 自动生成的 /docs 文档页面。
    APP_TITLE = "App name"

    # 服务监听地址。Docker 中通常使用 0.0.0.0，表示容器内服务可被外部访问。
    ALLOWED_HOST = environ.get("ALLOWED_HOST")

    # JWT、密码签名等安全逻辑会用到的密钥。真实上线时必须换成强随机字符串。
    SECRET_KEY = environ.get("SECRET_KEY")

    # bool("False") 在 Python 中也是 True，这是这个模板的一个学习重点和潜在问题。
    # 更稳的写法通常是 environ.get("DEBUG", "False").lower() == "true"。
    DEBUG = bool(environ.get("DEBUG"))

    # 服务端口。环境变量读出来是字符串，所以要用 int(...) 转成整数。
    ALLOWED_PORT = int(environ.get("PORT"))

    # 下面这些变量用于拼接 PostgreSQL 数据库连接地址。
    DB_USER = environ.get("POSTGRES_USER")
    DB_PASSWORD = environ.get("POSTGRES_PASSWORD")
    DB_DB = environ.get("POSTGRES_DB")
    DB_PORT = environ.get("POSTGRES_PORT")
    DB_HOST = environ.get("POSTGRES_HOST")

    # SQLAlchemy 使用的数据库连接字符串。
    # 语法结构：数据库类型+驱动://用户名:密码@主机:端口/数据库名
    DB_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DB}"
    )

    # 测试数据库名，通常用于 pytest 等测试场景。
    TEST_DB = environ.get("POSTGRES_TEST_DB")

    # 测试数据库连接字符串。
    TEST_DB_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB}"
    )

    # access token 有效期，单位是秒。这里是 30 分钟。
    ACCESS_TOKEN_EXPIRY_TIME = 60 * 30

    # refresh token 有效期，单位是秒。这里是 365 天。
    REFRESH_TOKEN_EXPIRY_TIME = 60 * 24 * 365

    # passlib 的密码哈希器。bcrypt 是常见的密码哈希算法。
    PASSWORD_HASHER = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # JWT 签名算法。HS256 表示用同一个 SECRET_KEY 进行签名和验证。
    JWT_ALGORITHM = "HS256"

    # Redis 地址。Docker 容器里通常是 redis；本地直接运行时通常是 localhost。
    REDIS_HOST = environ.get("REDIS_HOST", "localhost")

    # Redis 端口。Redis 默认端口是 6379。
    REDIS_PORT = environ.get("REDIS_PORT", "6379")

    # 分页默认大小。当前模板里还没有真正使用。
    PAGE_SIZE = 50


# 创建一个全局配置对象，其他文件通过 from app.settings import settings 使用。
settings = Settings()
