from fastapi import APIRouter

from auth.api import router as auth
from ecommerce.api import router as ecommerce

# 如果以后新增业务模块，可以像下面这样导入它的 router：
# from app_name.api import router as app_name


# APIRouter 是 FastAPI 的路由集合对象。
# 这个文件扮演“总路由表”的角色，把各个业务模块的路由集中到一起。
router = APIRouter()

# 把 auth 模块的路由挂载进总路由。
# main.py 再把这个总路由挂载到 /api/v1 下，所以最终路径是 /api/v1/auth/...
router.include_router(auth)

# 把电商数据平台路由挂载进总路由。
# 页面路径：/api/v1/ecommerce/dashboard
# 数据接口：/api/v1/ecommerce/metrics
router.include_router(ecommerce)

# 新模块路由可以继续 include：
# router.include_router(app_name)
