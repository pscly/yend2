# backend/app/crud/crud_user.py
from typing import Optional, List, Any, Dict, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # SQLAlchemy 1.4+ for async select
from sqlalchemy import update as sqlalchemy_update # for update statements
from sqlalchemy import delete as sqlalchemy_delete # for delete statements

from app.models.user import User as UserModel # 导入 SQLAlchemy 模型
from app.schemas.user import UserCreate, UserUpdate # 导入 Pydantic Schemas
from app.core.security import get_password_hash, verify_password # 导入密码处理函数

class CRUDUser:
    """
    用户模型的数据库操作 (CRUD) 类。
    所有方法都设计为异步，并接收一个 AsyncSession。
    """

    async def get_user_by_id(self, db: AsyncSession, *, user_id: int) -> Optional[UserModel]:
        """
        通过用户 ID 获取用户。
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, db: AsyncSession, *, username: str) -> Optional[UserModel]:
        """
        通过用户名获取用户。
        """
        stmt = select(UserModel).where(UserModel.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, *, email: str) -> Optional[UserModel]:
        """
        通过电子邮箱获取用户。
        """
        if not email: # 避免对 None 或空字符串进行查询
            return None
        stmt = select(UserModel).where(UserModel.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[UserModel]:
        """
        获取用户列表，支持分页。
        """
        stmt = select(UserModel).offset(skip).limit(limit).order_by(UserModel.id)
        result = await db.execute(stmt)
        return result.scalars().all() # scalars() 获取第一列，all() 转为列表

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> UserModel:
        """
        创建新用户。
        obj_in: UserCreate Pydantic schema 实例。
        """
        hashed_password = get_password_hash(obj_in.password)
        # 从 UserCreate schema 创建 SQLAlchemy 模型实例
        # Pydantic V2: .model_dump()
        # Pydantic V1: .dict()
        # db_obj = UserModel(**obj_in.model_dump(exclude={"password"}), hashed_password=hashed_password)
        # 或者更明确地：
        db_obj = UserModel(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=hashed_password,
            is_active=obj_in.is_active if obj_in.is_active is not None else True, # 处理可选字段的默认值
            is_superuser=obj_in.is_superuser,
            # is_verified=obj_in.is_verified if hasattr(obj_in, 'is_verified') and obj_in.is_verified is not None else False,
        )
        db.add(db_obj)
        await db.commit()  # 提交事务
        await db.refresh(db_obj) # 刷新实例以获取数据库生成的值 (如 ID, created_at)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: UserModel, # 要更新的 SQLAlchemy 用户模型实例
        obj_in: Union[UserUpdate, Dict[str, Any]] # Pydantic UserUpdate schema 或包含更新数据的字典
    ) -> UserModel:
        """
        更新用户信息。
        db_obj: 从数据库获取的现有用户模型实例。
        obj_in: 包含要更新字段的 Pydantic schema 或字典。
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else: # 是 Pydantic schema
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True) # Pydantic V2
            # update_data = obj_in.dict(exclude_unset=True, exclude_none=True) # Pydantic V1

        if "password" in update_data and update_data["password"]: # 如果提供了新密码
            hashed_password = get_password_hash(update_data["password"])
            db_obj.hashed_password = hashed_password
            del update_data["password"] # 从 update_data 中移除，避免下面 setattr 再次处理

        # 更新模型的其他字段
        for field, value in update_data.items():
            if hasattr(db_obj, field): # 确保字段存在于模型中
                setattr(db_obj, field, value)

        db.add(db_obj) # 将更改添加到会话
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, user_id: int) -> Optional[UserModel]:
        """
        通过 ID 删除用户。
        返回被删除的用户对象，如果用户不存在则返回 None。
        """
        user_to_delete = await self.get_user_by_id(db, user_id=user_id)
        if user_to_delete:
            await db.delete(user_to_delete)
            await db.commit()
        return user_to_delete

    # --- 认证与权限辅助方法 ---
    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[UserModel]:
        """
        用户认证。
        如果认证成功，返回用户对象，否则返回 None。
        """
        user = await self.get_user_by_username(db, username=username)
        if not user:
            return None
        # if not user.is_active: # 可以选择是否在这里检查账户激活状态
        #     return None # 或者在 API 端点层面处理
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: UserModel) -> bool:
        """检查用户账户是否已激活"""
        return user.is_active

    def is_superuser(self, user: UserModel) -> bool:
        """检查用户是否为超级管理员"""
        return user.is_superuser

# 创建一个 CRUDUser 类的实例，以便在其他地方 (如 API 端点) 导入和使用。
# from app.crud.base import CRUDBase # 如果你有一个通用的 CRUDBase
# user = CRUDBase[UserModel, UserCreate, UserUpdate](UserModel)
# 或者直接实例化：
user = CRUDUser()