import logging

import sqlalchemy
from databases import Database
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from .settings import settings


# databases.Database 提供异步数据库连接能力。
# main.py 中的 await db.connect() / await db.disconnect() 操作的就是这个对象。
db = Database(settings.DB_URL)

# SQLAlchemy 的 MetaData 用来保存所有表结构信息。
# Base 模型会复用这个 metadata，Alembic 也会依赖它识别表结构。
metadata = sqlalchemy.MetaData()

# create_engine 创建同步 SQLAlchemy 引擎。
# pool_size=3 表示连接池里最多保留 3 个常驻连接。
# max_overflow=0 表示连接池满了之后不额外创建临时连接。
engine = sqlalchemy.create_engine(settings.DB_URL, pool_size=3, max_overflow=0)

# 如果数据库不存在，就自动创建数据库。
# 学习项目里这样比较省事；生产项目通常会把数据库创建交给运维或部署脚本。
if not database_exists(engine.url):
    create_database(engine.url)

# sessionmaker 是“数据库会话工厂”。
# 每次调用 LocalSession()，都会创建一个新的数据库 Session。
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """给 FastAPI 接口使用的数据库依赖。

    语法解析：
    - yield 会把 db session 交给接口函数使用。
    - 接口执行完之后，会继续执行 finally 里的关闭逻辑。
    - 典型用法是：db: Session = Depends(get_db)
    """

    try:
        # 创建一个数据库会话，用来执行查询、插入、更新等操作。
        db = LocalSession()
        yield db
    except Exception as e:
        # 捕获数据库使用过程中的异常并写入日志。
        logging.error(e)
    finally:
        # 请求结束后关闭 session，释放数据库连接。
        # 注意：如果 LocalSession() 创建失败，这里 db 可能未定义，这是模板里的一个潜在问题。
        db.close()
