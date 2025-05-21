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
# from app.models.user import User as UserModel # 如果需要直接操作 User，但通常通过 user_id

# --- CRUDNavigationGroup Class ---
class CRUDNavigationGroup:
    """
    导航分组模型的数据库操作 (CRUD) 类。
    """

    async def get_group_by_id(
        self, db: AsyncSession, *, group_id: int, user_id: int
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
            .order_by(NavigationGroupModel.order_index, NavigationGroupModel.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_group_for_user(
        self, db: AsyncSession, *, obj_in: NavigationGroupCreate, user_id: int
    ) -> NavigationGroupModel:
        """为指定用户创建新的导航分组。"""
        db_obj_data = obj_in.model_dump()
        db_obj_data["user_id"] = user_id # 确保 user_id 被设置
        db_obj = NavigationGroupModel(**db_obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_group(
        self,
        db: AsyncSession,
        *,
        db_obj: NavigationGroupModel,
        obj_in: Union[NavigationGroupUpdate, Dict[str, Any]]
    ) -> NavigationGroupModel:
        """更新导航分组信息。"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)

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
        group_to_delete = await self.get_group_by_id(db, group_id=group_id, user_id=user_id)
        if group_to_delete:
            await db.delete(group_to_delete)
            await db.commit()
        return group_to_delete

# --- CRUDNavigationItem Class ---
class CRUDNavigationItem:
    """
    导航项模型的数据库操作 (CRUD) 类。
    """

    async def get_item_by_id(
        self, db: AsyncSession, *, item_id: int, user_id: int
    ) -> Optional[NavigationItemModel]:
        """通过导航项ID获取导航项，并验证其所有权。"""
        stmt = (
            select(NavigationItemModel)
            .join(NavigationGroupModel, NavigationItemModel.group_id == NavigationGroupModel.id)
            .where(
                NavigationItemModel.id == item_id,
                NavigationGroupModel.user_id == user_id # 通过关联的 group 验证 user_id
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_items_by_group_id(
        self, db: AsyncSession, *, group_id: int, user_id: int, skip: int = 0, limit: int = 200
    ) -> List[NavigationItemModel]:
        """获取指定导航分组下的所有导航项，并验证分组所有权。"""
        # 先验证分组是否属于该用户
        group_owner_check = await crud_navigation_group.get_group_by_id(db, group_id=group_id, user_id=user_id)
        if not group_owner_check:
            return [] # 或者抛出 HTTPException(status_code=404, detail="Group not found or not owned by user")

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
        group_owner_check = await crud_navigation_group.get_group_by_id(db, group_id=group_id, user_id=user_id)
        if not group_owner_check:
            return None # 或者抛出 HTTPException

        db_obj_data = obj_in.model_dump()
        db_obj_data['url'] = str(db_obj_data['url'])
        db_obj_data["group_id"] = group_id # 确保 group_id 被设置
        db_obj = NavigationItemModel(**db_obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_item(
        self,
        db: AsyncSession,
        *,
        db_obj: NavigationItemModel,
        obj_in: Union[NavigationItemUpdate, Dict[str, Any]]
    ) -> NavigationItemModel:
        """更新导航项信息。"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)

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
        """重新排序指定分组内的导航项。"""
        group_owner_check = await crud_navigation_group.get_group_by_id(db, group_id=group_id, user_id=user_id)
        if not group_owner_check:
            return False

        current_items_stmt = select(NavigationItemModel.id).where(NavigationItemModel.group_id == group_id)
        result = await db.execute(current_items_stmt)
        valid_item_ids_in_group = {item_id_tuple[0] for item_id_tuple in result.fetchall()}

        if not set(ordered_item_ids).issubset(valid_item_ids_in_group) or \
           len(ordered_item_ids) != len(valid_item_ids_in_group): # 确保所有项都被包含且没有多余项
            return False

        for index, item_id in enumerate(ordered_item_ids):
            stmt = (
                sqlalchemy_update(NavigationItemModel)
                .where(NavigationItemModel.id == item_id, NavigationItemModel.group_id == group_id)
                .values(order_index=index)
            )
            await db.execute(stmt)
        await db.commit()
        return True

# 创建 CRUD 类的实例
crud_navigation_group = CRUDNavigationGroup()
crud_navigation_item = CRUDNavigationItem()