from fastapi import HTTPException, status


# 这些变量是预先定义好的 HTTP 异常对象。
# 业务代码里可以直接 raise UserExist / raise InvalidCredentials。

# 400：请求参数有问题。这里表示用户邮箱已存在。
UserExist = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User with this email already exists",
)

# 401：未认证。这里表示登录邮箱或密码错误。
InvalidCredentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Email or password is incorrect. Incorrect login credentials",
)

# 401：token 过期。
# headers={"WWW-Authenticate": "Bearer"} 会告诉客户端这是 Bearer token 认证失败。
TokenExpired = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
    headers={"WWW-Authenticate": "Bearer"},
)

# 403：禁止访问。这里表示 token 或认证信息无法校验。
UnvalidatedCredentials = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# 404：资源不存在。这里表示找不到用户。
UserDoesNotExist = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Could not find user",
)
