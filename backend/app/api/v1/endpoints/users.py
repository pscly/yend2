# backend/app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app.api import deps # 依赖项 (如 get_async_db, get_current_active_user 等)
from app.crud.crud_user import user as crud_user # 用户 CRUD 操作
from app.schemas.user import UserCreate, UserPublic, UserUpdate # 用户 Pydantic schemas
from app.models.user import User as UserModel # SQLAlchemy 用户模型
from app.core.config import settings # 应用配置 (例如，是否允许开放注册)

router = APIRouter()

# --- 当前用户操作 ---

@router.get("/me", response_model=UserPublic, summary="获取当前用户信息")
async def read_user_me(
    current_user: UserModel = Depends(deps.get_current_active_user) # 依赖注入当前激活的用户
) -> UserPublic:
    """
    获取当前已认证用户（通过 Access Token）的公开信息。
    """
    # FastAPI 会自动将 UserModel 转换为 UserPublic schema
    return current_user


@router.put("/me", response_model=UserPublic, summary="更新当前用户信息")
async def update_user_me(
    *, # 星号表示后面的参数都是关键字参数
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: UserUpdate, # 从请求体中获取更新数据
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> UserPublic:
    """
    更新当前已认证用户的信息。
    用户只能更新自己的信息。
    """
    # 检查用户名或邮箱是否与他人冲突 (如果允许修改这些字段且它们是唯一的)
    if user_in.username and user_in.username != current_user.username:
        existing_user_by_username = await crud_user.get_user_by_username(db, username=user_in.username)
        if existing_user_by_username and existing_user_by_username.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, # 409 Conflict 更合适
                detail="该用户名已被其他用户使用。",
            )

    if user_in.email and user_in.email != current_user.email:
        existing_user_by_email = await crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user_by_email and existing_user_by_email.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该电子邮箱已被其他用户使用。",
            )

    updated_user = await crud_user.update(db=db, db_obj=current_user, obj_in=user_in)
    return updated_user


# --- 公开的用户注册 (如果允许) ---
# 你可以通过配置项 (例如 settings.USERS_OPEN_REGISTRATION) 来控制是否启用此端点
# if settings.USERS_OPEN_REGISTRATION: # 假设有这个配置
@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED, summary="用户注册")
async def register_new_user(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: UserCreate # 从请求体中获取用户注册信息
) -> UserPublic:
    """
    创建新用户账户（开放注册）。
    如果用户名或邮箱已存在，将返回错误。
    """
    existing_user_by_username = await crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # 或者 409 Conflict
            detail="该用户名已被注册。",
        )
    if user_in.email: # 只有当提供了 email 时才检查
        existing_user_by_email = await crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, # 或者 409 Conflict
                detail="该电子邮箱已被注册。",
            )

    # 可以在这里设置新注册用户的默认角色或状态，如果 UserCreate schema 中没有
    # 例如，确保 is_superuser 为 False
    user_in.is_superuser = False # 确保普通用户注册时不是超级用户
    # user_in.is_active = False # 如果需要邮箱验证后才激活

    new_user = await crud_user.create(db=db, obj_in=user_in)
    # (可选) 注册后发送欢迎邮件或验证邮件
    # send_new_account_email(email_to=new_user.email, username=new_user.username, password=user_in.password)
    return new_user


# --- 管理员操作的端点 (示例) ---
# 这些端点通常需要 `get_current_active_superuser` 依赖来保护

@router.get("/", response_model=List[UserPublic], summary=" (管理员) 获取用户列表")
async def read_users_list(
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_superuser) # 需要超级用户权限
) -> List[UserPublic]:
    """
    获取用户列表 (分页)。
    仅限超级管理员访问。
    """
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserPublic, summary=" (管理员) 获取指定用户信息")
async def read_user_by_id(
    user_id: int, # 从路径参数获取用户ID
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: UserModel = Depends(deps.get_current_active_superuser) # 需要超级用户权限
) -> UserPublic:
    """
    通过用户 ID 获取特定用户的信息。
    仅限超级管理员访问。
    """
    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到该用户。",
        )
    return user


@router.put("/{user_id}", response_model=UserPublic, summary=" (管理员) 更新指定用户信息")
async def update_user_by_id_as_admin(
    user_id: int,
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: UserUpdate, # 注意：这个 UserUpdate schema 可能需要调整，例如不允许管理员直接修改密码字段
    current_admin: UserModel = Depends(deps.get_current_active_superuser)
) -> UserPublic:
    """
    (管理员) 更新指定 ID 用户的信息。
    需要谨慎处理密码更新逻辑。
    """
    user_to_update = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到要更新的用户。",
        )

    # (管理员更新时) 检查用户名或邮箱是否与 *其他* 用户冲突
    if user_in.username and user_in.username != user_to_update.username:
        existing_user = await crud_user.get_user_by_username(db, username=user_in.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="该用户名已被其他用户使用。")

    if user_in.email and user_in.email != user_to_update.email:
        existing_user = await crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="该电子邮箱已被其他用户使用。")

    # 管理员通常不应该通过这个接口直接设置用户的明文密码。
    # 如果需要管理员重置密码，应该有专门的流程或接口。
    # 如果 user_in 中包含 password，需要特别处理或移除。
    if user_in.password is not None:
        # 可以选择移除密码更新，或者记录日志并通知需要单独流程
        # del user_in.password # 或者在 UserUpdate schema 中管理员版本里去掉 password 字段
        # 或者，如果你允许管理员设置密码（例如，用于初始设置或重置）：
        # updated_user = await crud_user.update(db=db, db_obj=user_to_update, obj_in=user_in)
        # 但 UserUpdate schema 通常不包含密码。
        # 一个更好的方式是，如果管理员要改密码，obj_in 中 password 为空，然后用专门的“重置密码”逻辑
        pass # 暂时忽略管理员通过此接口修改密码

    updated_user = await crud_user.update(db=db, db_obj=user_to_update, obj_in=user_in)
    return updated_user


@router.delete("/{user_id}", response_model=UserPublic, summary=" (管理员) 删除指定用户")
async def delete_user_by_id_as_admin(
    user_id: int,
    db: AsyncSession = Depends(deps.get_async_db),
    current_admin: UserModel = Depends(deps.get_current_active_superuser)
) -> UserPublic:
    """
    (管理员) 删除指定 ID 的用户。
    这是一个危险操作，请谨慎使用。
    """
    user_to_delete = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到要删除的用户。",
        )
    if user_to_delete.id == current_admin.id: # 防止管理员删除自己
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员不能删除自己的账户。",
        )

    deleted_user = await crud_user.remove(db=db, user_id=user_id)
    if not deleted_user: # 再次确认，理论上不会发生，因为上面已经检查过了
        raise HTTPException(status_code=500, detail="删除用户失败。")
    return deleted_user