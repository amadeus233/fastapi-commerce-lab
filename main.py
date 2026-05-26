import logging

import uvicorn
from fastapi import FastAPI

from app.routes import router
from app.settings import settings
from app.db import LocalSession, db, metadata, engine
from app import models
from ecommerce.services import seed_ecommerce_data


# FastAPI(...) 会创建整个 Web 应用对象。
# title 会显示在 Swagger 文档页面，也就是 /docs 页面顶部。
app = FastAPI(title=settings.APP_TITLE)

# include_router 用来把其他文件里定义好的接口“挂载”到主应用上。
# prefix="/api/v1" 表示所有接口都会带上 /api/v1 前缀，方便以后做接口版本管理。
app.include_router(router, prefix="/api/v1")


# @app.on_event("startup") 是 FastAPI 的生命周期钩子。
# 语法解析：
# - @xxx 是装饰器，会把下面的函数注册给 FastAPI。
# - "startup" 表示应用启动时执行。
# - async def 表示这是异步函数，可以在里面 await 异步 I/O 操作。
@app.on_event("startup")
async def startup():
    # db.connect() 会建立数据库连接池。
    # await 的意思是“等待这个异步操作完成后再继续”。
    await db.connect()

    # 导入 app.models 后，metadata 会收集 auth/ecommerce 等模块里的所有模型。
    # create_all 会根据模型在 PostgreSQL 中创建缺失的数据表。
    metadata.create_all(engine)

    # 启动时初始化电商演示数据。
    # 这里使用独立的 SQLAlchemy Session，把数据写入 PostgreSQL。
    session = LocalSession()
    try:
        seed_ecommerce_data(session)
    finally:
        session.close()


# shutdown 是和 startup 对应的关闭生命周期钩子。
# 当服务停止、重启或进程退出时，FastAPI 会调用这个函数。
@app.on_event("shutdown")
async def shutdown():
    # 断开数据库连接，释放连接池资源，避免服务退出后连接残留。
    await db.disconnect()


# __name__ 是 Python 自动提供的特殊变量。
# 当你直接运行 python main.py 时，__name__ == "__main__"。
# 当别的文件 import main 时，这段启动代码不会执行。
if __name__ == "__main__":
    """服务启动配置。"""

    # uvicorn 是 ASGI 服务器，负责真正监听端口、接收 HTTP 请求。
    # FastAPI 负责定义接口逻辑；uvicorn 负责把 FastAPI 应用跑起来。
    uvicorn.run(
        # "main:app" 的意思是：从 main.py 这个模块中找到名为 app 的 FastAPI 对象。
        app="main:app",
        # host 来自环境配置。0.0.0.0 表示允许外部访问这个服务。
        host=settings.ALLOWED_HOST,
        # debug 控制调试模式。注意：当前 settings.py 中 DEBUG 的布尔转换有潜在问题。
        debug=settings.DEBUG,
        # port 是服务监听端口，默认来自 .env 中的 PORT=11000。
        port=settings.ALLOWED_PORT,
        # reload=True 适合开发环境：代码变化后自动重启服务。
        reload=True,
        # 日志级别设为 INFO，能看到启动、请求、普通运行日志。
        log_level=logging.INFO,
        # 让终端日志带颜色，便于阅读。
        use_colors=True,
    )
