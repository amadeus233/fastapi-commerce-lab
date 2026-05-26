from .base import Base

# 导入 auth 模块里的所有模型。
# 这样 Alembic 和 metadata.create_all(engine) 才能“看见”这些表结构。
from auth.models import *
from ecommerce.models import *

# 如果以后新增业务模块，比如 article/models.py，需要在这里继续导入：
# from app_name.models import *
