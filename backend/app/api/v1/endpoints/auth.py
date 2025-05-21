# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # FastAPI 提供的用于处理表单数据的类
from sqlalchemy.ext.asyncio import AsyncSession # 异步数据库会话
from datetime import timedelta

from app.api import deps # 导入依赖项 (如 get_async_db)
from app.core import security # 导入安全相关的函数 (token 创建、密码验证)
from app.core.config import settings # 导入应用配置
from app.schemas.user import Token, UserPublic # 导入 Pydantic schemas
from app.crud.crud_user import user as crud_user # 导入用户 CRUD 操作实例
from app.models.user import User as UserModel # 导入 SQLAlchemy 用户模型 (用于类型提示)

router = APIRouter()

@router.post("/login", response_model=Token, summary="用户登录获取访问令牌")
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_async_db), # 注入异步数据库会话
    form_data: OAuth2PasswordRequestForm = Depends() # 从请求表单中获取 username 和 password
) -> Token:
    """
    OAuth2兼容的登录接口，用于获取访问令牌 (Access Token)。

    客户端应使用 `application/x-www-form-urlencoded` 类型提交 `username` 和 `password`。
    成功后返回包含 `access_token` 和 `token_type` 的 JSON 对象。
    """
    user = await crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误", # 更友好的错误提示
            headers={"WWW-Authenticate": "Bearer"}, # 符合 OAuth2 标准
        )
    if not crud_user.is_active(user): # 检查用户是否激活
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # 或者 403 Forbidden
            detail="用户账户未激活",
        )

    # 创建 access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.username, # 或者 user.id，取决于你的 token sub 声明策略
        # 你也可以在这里传递其他信息到 token payload，例如 user_id
        # extra_data={"user_id": user.id} # (需要在 create_access_token 函数中支持)
        expires_delta=access_token_expires
    )

    # (可选) 更新用户最后登录时间
    # user.last_login_at = datetime.now(timezone.utc)
    # await crud_user.update(db, db_obj=user, obj_in={"last_login_at": user.last_login_at})
    # 注意: 上述 update 可能需要调整，确保只更新特定字段

    return Token(access_token=access_token, token_type="bearer")


@router.post("/test-token", response_model=UserPublic, summary="测试访问令牌有效性")
async def test_token(
    current_user: UserModel = Depends(deps.get_current_active_user) # 依赖注入当前激活的用户
) -> UserPublic:
    """
    一个受保护的端点，用于测试客户端提供的 Access Token 是否有效。
    如果 token 有效且用户已激活，则返回当前用户的信息。
    """
    # FastAPI 会自动将 UserModel 转换为 UserPublic schema
    return current_user


# (可选) 如果你需要一个刷新 token 的端点
# @router.post("/refresh-token", response_model=Token, summary="刷新访问令牌")
# async def refresh_access_token(
#     # 你需要实现一个获取刷新令牌的依赖或逻辑
#     # 例如，从请求体中获取 refresh_token，验证它，然后颁发新的 access_token
#     # refresh_token_payload: dict = Depends(validate_refresh_token_dependency)
# ):
#     # username = refresh_token_payload.get("sub")
#     # user = await crud_user.get_user_by_username(db, username=username)
#     # if not user or not user.is_active:
#     #     raise HTTPException(...)
#     # new_access_token = security.create_access_token(...)
#     # return Token(access_token=new_access_token, token_type="bearer")
#     raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="刷新令牌功能尚未实现")