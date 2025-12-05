"""
认证核心模块 - 简单实用，不过度设计

功能：
- 从 JSON 文件加载用户
- bcrypt 密码验证
- JWT token 生成和验证
- FastAPI 依赖注入
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token 认证方案
security = HTTPBearer()

# 用户缓存（启动时加载一次，避免每次请求都读文件）
_users_cache: dict = {}


def get_users_file_path() -> str:
    """获取用户配置文件路径"""
    # users.json 位于 backend/ 目录下
    return os.path.join(os.path.dirname(__file__), "../../users.json")


def load_users() -> dict:
    """
    从 JSON 文件加载用户列表

    Returns:
        dict: {username: user_dict} 格式的用户字典
    """
    global _users_cache

    users_file = get_users_file_path()

    if not os.path.exists(users_file):
        print(f"[Auth] 警告: 用户配置文件不存在: {users_file}")
        return {}

    try:
        with open(users_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            _users_cache = {u["username"]: u for u in data.get("users", [])}
            print(f"[Auth] 已加载 {len(_users_cache)} 个用户")
            return _users_cache
    except Exception as e:
        print(f"[Auth] 加载用户配置失败: {e}")
        return {}


def reload_users() -> dict:
    """
    重新加载用户配置（用于热更新）
    """
    global _users_cache
    _users_cache = {}
    return load_users()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配

    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 存储的 bcrypt 哈希密码

    Returns:
        bool: 密码是否正确
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码的 bcrypt 哈希值

    Args:
        password: 明文密码

    Returns:
        str: bcrypt 哈希密码
    """
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    验证用户凭据

    Args:
        username: 用户名
        password: 明文密码

    Returns:
        dict: 用户信息，验证失败返回 None
    """
    # 确保用户已加载
    if not _users_cache:
        load_users()

    user = _users_cache.get(username)
    if not user:
        return None

    if not verify_password(password, user.get("password_hash", "")):
        return None

    return user


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """
    创建 JWT access token

    Args:
        data: 要编码到 token 中的数据
        expires_delta: token 有效期

    Returns:
        str: JWT token 字符串
    """
    from app.core.config import settings

    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm="HS256"
    )
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    从 JWT token 获取当前用户 - 作为 FastAPI 依赖注入使用

    Args:
        credentials: HTTP Bearer token

    Returns:
        dict: 包含 username 的用户信息

    Raises:
        HTTPException: 401 如果 token 无效
    """
    from app.core.config import settings

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=["HS256"]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 验证用户是否仍然存在于配置中
    if not _users_cache:
        load_users()

    user = _users_cache.get(username)
    if user is None:
        raise credentials_exception

    return {"username": username}


# 可选的认证依赖 - 用于某些端点允许匿名访问
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """
    可选的用户认证 - 如果没有提供 token 则返回 None
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
