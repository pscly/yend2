# backend/app/api/deps.py
import logging
from typing import Generator, Optional, AsyncGenerator, Union, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SyncSession # 同步会话类型
from sqlalchemy.ext.asyncio import AsyncSession    # 异步会话类型
from jose import JWTError, ExpiredSignatureError
from pydantic import ValidationError

from app.db.session import SyncSessionLocal, AsyncSessionLocal # 导入两种会话工厂
from app.core import security
from app.core.config import settings
from app.schemas.user import TokenData, UserPublic # <--- 确认这里导入了 TokenData 和 UserPublic
from app.crud.crud_user import user as crud_user # 导入 crud_user 实例
from app.models.user import User as UserModel # 导入模型

# 配置日志记录器
logger = logging.getLogger(__name__)


# --- OAuth2 密码模式 ---
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
)

# --- 数据库会话依赖 ---
def get_sync_db() -> Generator[SyncSession, None, None]:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话的依赖函数。
    """
    if not AsyncSessionLocal:
        raise RuntimeError("异步数据库会话 (AsyncSessionLocal) 未正确配置。请检查 DATABASE_URL 是否为异步 DSN。")

    # 创建新的异步会话
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"数据库会话异常: {str(e)}", exc_info=True)
        try:
            await session.rollback()  # 发生异常时回滚
        except Exception as rollback_error:
            logger.error(f"回滚会话时出错: {str(rollback_error)}")
        raise
    finally:
        try:
            await session.close()  # 确保会话被关闭
        except Exception as close_error:
            logger.error(f"关闭会话时出错: {str(close_error)}")


# --- 当前用户依赖 (异步) ---
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(reusable_oauth2)
) -> UserModel: # 返回 UserModel 实例
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="令牌已过期",
        headers={"WWW-Authenticate": "Bearer error=\"invalid_token\", error_description=\"The token has expired\""},
    )

    try:
        # 解码令牌
        payload = security.decode_access_token(token)
        if payload is None:
            logger.warning(f"无效的访问令牌: {token[:10]}...")
            raise credentials_exception

        # 提取用户标识符
        username: Optional[str] = payload.get("sub")  # 'sub' claim in JWT
        if username is None:
            logger.warning("令牌中缺少'sub'声明")
            raise credentials_exception

        # 使用TokenData schema验证payload结构
        try:
            token_data = TokenData(
                sub=username,
                user_id=payload.get("user_id"),
                exp=payload.get("exp"),
                iat=payload.get("iat"),
                jti=payload.get("jti"),
                iss=payload.get("iss")
            )
        except ValidationError as e:
            logger.warning(f"令牌数据验证失败: {str(e)}")
            raise credentials_exception

        # 获取用户
        user = await crud_user.get_user_by_username(db, username=username)
        if user is None:
            logger.warning(f"找不到用户: {username}")
            raise credentials_exception

        # 记录成功的认证
        client_ip = str(request.client)
        try:
            if hasattr(request, 'headers') and 'x-forwarded-for' in request.headers:
                client_ip = request.headers['x-forwarded-for']
        except:
            pass

        logger.info(f"用户 {username} 认证成功 (IP: {client_ip})")

        return user

    except ExpiredSignatureError:
        logger.warning("令牌已过期")
        raise expired_token_exception
    except JWTError as e:
        logger.warning(f"JWT错误: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"认证过程中发生意外错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证过程中发生内部错误"
        )

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    验证当前用户是否处于活动状态。
    """
    if not crud_user.is_active(current_user):
        logger.warning(f"非活动用户尝试访问: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户未激活"
        )
    return current_user

async def get_current_active_superuser(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    """
    验证当前用户是否为超级管理员。
    """
    if not crud_user.is_superuser(current_user):
        logger.warning(f"非管理员用户 {current_user.username} 尝试访问管理员资源")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户没有足够的权限",
        )
    return current_user

# 可选：允许匿名访问的依赖项
async def get_optional_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    token: Optional[str] = Depends(reusable_oauth2),
) -> Optional[UserModel]:
    """
    尝试获取当前用户，但如果没有提供有效令牌，则返回None而不是抛出异常。
    用于允许匿名访问但仍能识别已认证用户的端点。
    """
    if not token:
        return None

    try:
        return await get_current_user(request=request, db=db, token=token)
    except HTTPException:
        return None