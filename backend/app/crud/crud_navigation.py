# backend/app/crud/crud_navigation.py
from typing import Optional, List, Any, Dict, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, and_

from app.models.navigation import NavigationGroup as NavigationGroupModel
from app.models.navigation import NavigationItem as NavigationItemModel
from app.schemas.navigation import (
    NavigationGroupCreate,
    NavigationGroupUpdate,
    NavigationItemCreate,
    NavigationItemUpdate,
)
from app.models.user import User as UserModel # 用于关联用户

class CRUDNavigationGroup:
    """
    导航分组模型的数据库操作 (CRUD) 类。
    """

    async def get_group_by_id(
        self, db: AsyncSession, *, group_id: int, user_id: int # 确保分组属于该用户
    ) -> Optional[NavigationGroupModel]:
        """通过分组ID和用户ID获取导航分组。"""
        stmt = select(NavigationGroupModel).where(
            NavigationGroupModel.id == group_id,
            NavigationGroupModel.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_groups_by_user_id(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[NavigationGroupModel]:
        """获取指定用户的所有导航分组，支持分页和排序。"""
        stmt = (
            select(NavigationGroupModel)
            .where(NavigationGroupModel.user_id == user_id)
            .order_by(NavigationGroupModel.order_index, NavigationGroupModel.created_at) # 按排序索引和创建时间排序
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_group_for_user(
        self, db: AsyncSession, *, obj_in: NavigationGroupCreate, user_id: int
    ) -> NavigationGroupModel:
        """为指定用户创建新的导航分组。"""
        db_obj = NavigationGroupModel(
            **obj_in.model_dump(), # Pydantic V2
            # **obj_in.dict(), # Pydantic V1
            user_id=user_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_group(
        self,
        db: AsyncSession,
        *,
        db_obj: NavigationGroupModel, # 要更新的 SQLAlchemy 模型实例
        obj_in: Union[NavigationGroupUpdate, Dict[str, Any]]
    ) -> NavigationGroupModel:
        """更新导航分组信息。"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True) # Pydantic V2
            # update_data = obj_in.dict(exclude_unset=True, exclude_none=True) # Pydantic V1

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove_group(
        self, db: AsyncSession, *, group_id: int, user_id: int
    ) -> Optional[NavigationGroupModel]:
        """删除属于特定用户的导航分组。"""
        # 首先获取对象，确保它属于该用户，然后删除
        # cascade="all, delete-orphan" 在模型定义中会处理其下的 items
        group_to_delete = await self.get_group_by_id(db, group_id=group_id, user_id=user_id)
        if group_to_delete:
            await db.delete(group_to_delete)
            await db.commit()
        return group_to_delete


class CRUDNavigationItem:
    """
    导航项模型的数据库操作 (CRUD) 类。
    """

    async def get_item_by_id(
        self, db: AsyncSession, *, item_id: int, user_id: int # 确保操作的是该用户的导航项
    ) -> Optional[NavigationItemModel]:
        """通过导航项ID获取导航项，并验证其所有权。"""
        stmt = (
            select(NavigationItemModel)
            .join(NavigationGroupModel, NavigationItemModel.group_id == NavigationGroupModel.id) # 通过group确保用户所有权
            .where(
                NavigationItemModel.id == item_id,
                NavigationGroupModel.user_id == user_id
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_items_by_group_id(
        self, db: AsyncSession, *, group_id: int, user_id: int, skip: int = 0, limit: int = 200 # 导航项通常不会非常多
    ) -> List[NavigationItemModel]:
        """获取指定导航分组下的所有导航项，并验证分组所有权。"""
        # 首先确认分组存在且属于用户
        group = await crud_navigation_group.get_group_by_id(db, group_id=group_id, user_id=user_id)
        if not group:
            return [] # 或者抛出异常

        stmt = (
            select(NavigationItemModel)
            .where(NavigationItemModel.group_id == group_id)
            .order_by(NavigationItemModel.order_index, NavigationItemModel.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_item_in_group(
        self, db: AsyncSession, *, obj_in: NavigationItemCreate, group_id: int, user_id: int
    ) -> Optional[NavigationItemModel]:
        """在指定导航分组下创建新的导航项，并验证分组所有权。"""
        # 确认分组存在且属于用户
        group = await crud_navigation_group.get_group_by_id(db, group_id=group_id, user_id=user_id)
        if not group:
            return None # 或者抛出异常，表示分组不存在或不属于该用户

        db_obj = NavigationItemModel(
            **obj_in.model_dump(), # Pydantic V2
            # **obj_in.dict(), # Pydantic V1
            group_id=group_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_item(
        self,
        db: AsyncSession,
        *,
        db_obj: NavigationItemModel, # 要更新的 SQLAlchemy 模型实例
        obj_in: Union[NavigationItemUpdate, Dict[str, Any]]
    ) -> NavigationItemModel:
        """更新导航项信息。"""
        # (在调用此方法前，应已通过 get_item_by_id 验证了所有权)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True) # Pydantic V2
            # update_data = obj_in.dict(exclude_unset=True, exclude_none=True) # Pydantic V1

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove_item(
        self, db: AsyncSession, *, item_id: int, user_id: int
    ) -> Optional[NavigationItemModel]:
        """删除导航项，并验证其所有权。"""
        item_to_delete = await self.get_item_by_id(db, item_id=item_id, user_id=user_id)
        if item_to_delete:
            await db.delete(item_to_delete)
            await db.commit()
        return item_to_delete

    async def reorder_items_in_group(
        self, db: AsyncSession, *, group_id: int, user_id: int, ordered_item_ids: List[int]
    ) -> bool:
        """
        重新排序指定分组内的导航项。
        ordered_item_ids: 包含导航项ID的列表，按新的顺序排列。
        """
        group = await crud_navigation_group.get_group_by_id(db, group_id=group_id, user_id=user_id)
        if not group:
            return False # 分组不存在或不属于用户

        # 获取该分组下所有当前存在的导航项，用于验证 ID 是否有效
        current_items_stmt = select(NavigationItemModel.id).where(NavigationItemModel.group_id == group_id)
        result = await db.execute(current_items_stmt)
        valid_item_ids_in_group = {item_id_tuple[0] for item_id_tuple in result.fetchall()}

        if not set(ordered_item_ids).issubset(valid_item_ids_in_group):
            # 如果传入的 ID 列表包含不属于该分组的项，则操作失败
            # 或者，如果传入的ID数量与分组内实际项数量不匹配 (除非允许部分排序)
            # 这里简化为：所有传入的 ID 必须有效且属于该分组
            return False # 或者抛出错误

        for index, item_id in enumerate(ordered_item_ids):
            stmt = (
                sqlalchemy_update(NavigationItemModel)
                .where(NavigationItemModel.id == item_id, NavigationItemModel.group_id == group_id) # 双重保险
                .values(order_index=index)
            )
            await db.execute(stmt)

        await db.commit()
        return True

# 创建 CRUD 类的实例
crud_navigation_group = CRUDNavigationGroup()
crud_navigation_item = CRUDNavigationItem()