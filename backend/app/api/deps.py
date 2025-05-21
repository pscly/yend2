# backend/app/api/deps.py
from typing import Generator, Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SyncSession # 同步会话类型
from sqlalchemy.ext.asyncio import AsyncSession    # 异步会话类型
from jose import JWTError, ExpiredSignatureError

from app.db.session import SyncSessionLocal, AsyncSessionLocal # 导入两种会话工厂
from app.core import security
from app.core.config import settings
from app.schemas.user import TokenData, UserPublic
from app.crud.crud_user import user as crud_user
from app.models.user import User as UserModel


# --- OAuth2 密码模式 ---
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    # auto_error=True # 默认为 True, token 无效或缺失时直接抛出 401
)

# --- 数据库会话依赖 ---

# 同步数据库会话依赖 (用于同步端点或 Alembic 等)
def get_sync_db() -> Generator[SyncSession, None, None]:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 异步数据库会话依赖 (推荐用于 FastAPI 异步端点)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    if not AsyncSessionLocal:
        raise RuntimeError("异步数据库会话 (AsyncSessionLocal) 未正确配置。请检查 DATABASE_URL 是否为异步 DSN。")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 可以选择在这里提交事务，如果所有操作都在依赖的生命周期内完成
            # await session.commit()
        except Exception:
            # await session.rollback() # 如果发生异常则回滚
            raise
        # finally:
            # session.close() # AsyncSessionLocal() as session 已经处理了关闭


# 为了方便，我们可以创建一个通用的 get_db，但通常在端点中显式选择
# 如果你的应用完全是异步的，可以直接让 get_db = get_async_db
# 或者根据端点是同步还是异步来选择
# 这里我们暂时不定义通用的 get_db，让端点自己选择

# --- 当前用户依赖 (这里以异步为例，因为 FastAPI 端点通常是异步的) ---
async def get_current_user(
    db: AsyncSession = Depends(get_async_db), # 使用异步数据库会话
    token: str = Depends(reusable_oauth2)
) -> Optional[UserModel]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer error=\"invalid_token\", error_description=\"The token has expired\""},
    )

    try:
        payload = security.decode_access_token(token)
        if payload is None: # 包括了JWTError但非ExpiredSignatureError的情况
            raise credentials_exception
    except ExpiredSignatureError: # 特别处理token过期
        raise expired_token_exception
    except JWTError: # 其他JWT错误
        raise credentials_exception


    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception

    # 你也可以在 token 中存储 user_id，然后通过 user_id 查询
    # user_id_from_token: Optional[int] = payload.get("user_id")
    # token_data = TokenData(username=username, user_id=user_id_from_token)
    token_data = TokenData(username=username) # 简化

    # 注意：crud_user 中的方法也需要是异步的才能配合 await
    # 这里我们假设 crud_user.get_user_by_username_async 是一个异步方法
    # 如果 crud_user 是同步的，你需要用 run_in_threadpool 或者让 crud 也异步
    user = await crud_user.get_user_by_username_async(db, username=token_data.username) # 假设有异步版本
    # 如果 crud_user 是同步的，并且你想在异步函数中使用它:
    # from fastapi.concurrency import run_in_threadpool
    # user = await run_in_threadpool(crud_user.get_user_by_username, db_sync_session_somehow, username=token_data.username)
    # 但更好的方式是整个调用链都是异步的。

    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    # 同样，crud_user.is_superuser 可能也需要是异步的或在线程池中运行
    # is_super = await run_in_threadpool(crud_user.is_superuser, current_user)
    is_super = crud_user.is_superuser(current_user) # 假设 is_superuser 是快速同步操作
    if not is_super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user