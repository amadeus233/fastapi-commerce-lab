from fastapi import APIRouter


# prefix="/auth" 表示这个文件里的接口都会以 /auth 开头。
# main.py 还会统一加 /api/v1，所以最终访问路径是 /api/v1/auth/ok。
router = APIRouter(prefix="/auth")


@router.get("/ok")
async def ok() -> str:
    # 一个最小健康检查接口，用来确认 auth 路由是否成功挂载。
    # 返回值标注 -> str 表示这个函数预期返回字符串。
    return "ok"
