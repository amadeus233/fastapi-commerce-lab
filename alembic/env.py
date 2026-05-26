from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.settings import settings

# Alembic 的 Config 对象，负责读取 alembic.ini 里的迁移配置。
config = context.config

# 用项目 settings.py 中的 DB_URL 覆盖 alembic.ini 里的占位数据库地址。
# 这样迁移命令会连接 .env 指定的 PostgreSQL。
config.set_main_option("sqlalchemy.url", settings.DB_URL)

# 根据 alembic.ini 中的 logging 配置初始化日志。
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入模型集合，让 Alembic 能发现 SQLAlchemy 模型。
# autogenerate 自动生成迁移脚本时会比较 target_metadata 和真实数据库结构。
from app import models
target_metadata = models.Base.metadata

# 如果有其他 Alembic 配置项，也可以从 config 中读取。
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """离线模式运行迁移。

    离线模式只需要数据库 URL，不需要真实建立数据库连接。
    它通常用于生成 SQL 脚本，而不是直接修改数据库。

    context.execute(...) 会把 SQL 输出到脚本中。

    """

    url = config.get_main_option("sqlalchemy.url")

    # context.configure 用来告诉 Alembic 当前迁移上下文怎么运行。
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # begin_transaction 开启迁移事务。
    with context.begin_transaction():
        # 执行迁移脚本。
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式运行迁移。

    在线模式会真实连接数据库，并直接执行迁移。

    """

    # 根据 alembic.ini 和 settings.DB_URL 创建数据库连接引擎。
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 建立数据库连接，并把连接交给 Alembic。
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# 根据当前运行模式选择离线迁移或在线迁移。
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
