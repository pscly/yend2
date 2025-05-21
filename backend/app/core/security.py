# backend/app/core/security.py
import uuid
import logging
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union, Dict
from jose import jwt, JWTError

from app.core.config import settings # 导入配置

# 配置日志记录器
logger = logging.getLogger(__name__)

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
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    创建 JWT access token.
    subject: 可以是用户名、用户ID等唯一标识符。
    expires_delta: 可选的过期时间增量，如果不提供则使用配置中的默认值。
    extra_claims: 可选的额外声明，如用户角色等。
    """
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # 基本声明
    to_encode = {
        "exp": expire,                # 过期时间 (必需)
        "iat": now,                   # 令牌发布时间
        "sub": str(subject),          # 主题 (通常是用户ID)
        "jti": str(uuid.uuid4()),     # JWT ID (唯一标识符，防止重放攻击)
        "iss": "yend2-backend"        # 发行者
    }

    # 添加额外声明
    if extra_claims:
        for key, value in extra_claims.items():
            if key not in to_encode:  # 避免覆盖标准声明
                to_encode[key] = value

    # 编码并返回
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建JWT令牌时出错: {str(e)}", exc_info=True)
        raise

def decode_access_token(token: str) -> Optional[dict]:
    """
    解码 JWT access token.
    如果解码失败或token过期，返回 None。
    """
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "verify_aud": False,  # 不验证受众
                "leeway": 10  # 允许10秒的时钟偏差
            }
        )
        return payload
    except JWTError as e: # 包括 ExpiredSignatureError, InvalidTokenError 等
        logger.warning(f"JWT令牌解码失败: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"JWT令牌解码时发生意外错误: {str(e)}", exc_info=True)
        return None