# backend/app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from jose import jwt, JWTError

from app.core.config import settings # 导入配置

# --- 密码哈希 ---
# 推荐使用 bcrypt 或 argon2
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256" # JWT 签名算法
# ACCESS_TOKEN_EXPIRE_MINUTES 在 settings 中定义

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception: # 例如 passlib.exc.UnknownHashError
        return False

def get_password_hash(password: str) -> str:
    """生成密码的哈希值"""
    return pwd_context.hash(password)


# --- JWT Token ---
def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT access token.
    subject: 可以是用户名、用户ID等唯一标识符。
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)} # "sub" (subject) 是标准声明
    # 你也可以添加其他自定义声明，例如用户ID，角色等
    # to_encode["user_id"] = user_id_if_available
    # to_encode["roles"] = ["user"]
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    解码 JWT access token.
    如果解码失败或token过期，返回 None。
    """
    try:
        # leeway 参数可以容忍几秒钟的时钟偏差
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM], leeway=10)
        return payload
    except JWTError: # 包括 ExpiredSignatureError, InvalidTokenError 等
        return None