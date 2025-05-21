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
from app.schemas.user import TokenData, UserPublic # <--- 确认这里导入了 TokenData 和 UserPublic
from app.crud.crud_user import user as crud_user # 导入 crud_user 实例
from app.models.user import User as UserModel # 导入模型


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
    if not AsyncSessionLocal:
        raise RuntimeError("异步数据库会话 (AsyncSessionLocal) 未正确配置。请检查 DATABASE_URL 是否为异步 DSN。")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback() # 发生异常时回滚
            raise
        # finally: # async with 语句会自动处理关闭
            # await session.close()


# --- 当前用户依赖 (异步) ---
async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(reusable_oauth2)
) -> UserModel: # 返回 UserModel 实例
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
        if payload is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise expired_token_exception
    except JWTError:
        raise credentials_exception

    username: Optional[str] = payload.get("sub") # 'sub' claim in JWT
    if username is None:
        raise credentials_exception

    # 使用 TokenData schema 验证 payload 的结构 (可选，但良好实践)
    # try:
    #     token_data = TokenData(sub=username, user_id=payload.get("user_id"))
    # except ValidationError: # Pydantic ValidationError
    #     raise credentials_exception
    # 我们在 create_access_token 时只用了 sub=username

    user = await crud_user.get_user_by_username(db, username=username) # 假设 crud_user 已改为异步
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not crud_user.is_active(current_user): # crud_user.is_active 是同步的
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    if not crud_user.is_superuser(current_user): # crud_user.is_superuser 是同步的
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user