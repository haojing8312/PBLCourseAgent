"""
认证 API 端点

端点：
- POST /api/v1/auth/login - 登录获取 token
- GET /api/v1/auth/me - 获取当前用户信息
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import authenticate_user, create_access_token, get_current_user
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """登录成功响应"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用户信息响应"""
    username: str


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    用户登录

    使用用户名和密码换取 JWT access token。

    Args:
        request: 包含 username 和 password 的登录请求

    Returns:
        TokenResponse: 包含 access_token 的响应

    Raises:
        HTTPException: 401 如果用户名或密码错误
    """
    user = authenticate_user(request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建 JWT token
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(hours=settings.jwt_expire_hours)
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息

    需要在请求头中提供有效的 Bearer token。

    Returns:
        UserResponse: 包含 username 的用户信息
    """
    return UserResponse(username=current_user["username"])
