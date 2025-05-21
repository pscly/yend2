# backend/app/crud/crud_push.py
from typing import Optional, List, Any, Dict, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, and_

from app.models.push import (
    PushSource as PushSourceModel,
    PushSubscription as PushSubscriptionModel,
    PushMessage as PushMessageModel,
)
from app.schemas.push import (
    PushSourceCreate,
    PushSourceUpdate,
    PushSubscriptionCreate,
    PushSubscriptionUpdate,
    # PushMessageCreate is usually not directly used for API,
    # messages are created internally based on webhook or other triggers.
)
from app.models.user import User as UserModel # For type hinting if needed

# --- CRUD for PushSource (通常由管理员操作) ---
class CRUDPushSource:
    async def get_source_by_id(self, db: AsyncSession, *, source_id: int) -> Optional[PushSourceModel]:
        stmt = select(PushSourceModel).where(PushSourceModel.id == source_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_source_by_name(self, db: AsyncSession, *, name: str) -> Optional[PushSourceModel]:
        stmt = select(PushSourceModel).where(PushSourceModel.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    # 如果 PushSource 模型中有 identifier 字段用于 webhook
    # async def get_source_by_identifier(self, db: AsyncSession, *, identifier: str) -> Optional[PushSourceModel]:
    #     stmt = select(PushSourceModel).where(PushSourceModel.identifier == identifier)
    #     result = await db.execute(stmt)
    #     return result.scalar_one_or_none()

    async def get_multi_sources(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, only_active: bool = False
    ) -> List[PushSourceModel]:
        stmt = select(PushSourceModel).order_by(PushSourceModel.name).offset(skip).limit(limit)
        if only_active:
            stmt = stmt.where(PushSourceModel.is_active == True)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_source(self, db: AsyncSession, *, obj_in: PushSourceCreate) -> PushSourceModel:
        db_obj = PushSourceModel(**obj_in.model_dump()) # Pydantic V2
        # db_obj = PushSourceModel(**obj_in.dict()) # Pydantic V1
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_source(
        self, db: AsyncSession, *, db_obj: PushSourceModel, obj_in: Union[PushSourceUpdate, Dict[str, Any]]
    ) -> PushSourceModel:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True) # Pydantic V2

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove_source(self, db: AsyncSession, *, source_id: int) -> Optional[PushSourceModel]:
        source_to_delete = await self.get_source_by_id(db, source_id=source_id)
        if source_to_delete:
            # cascade="all, delete-orphan" in PushSource model handles related subscriptions and messages_originated
            await db.delete(source_to_delete)
            await db.commit()
        return source_to_delete

# --- CRUD for PushSubscription (用户订阅操作) ---
class CRUDPushSubscription:
    async def get_subscription_by_id(self, db: AsyncSession, *, subscription_id: int, user_id: int) -> Optional[PushSubscriptionModel]:
        """获取特定用户的特定订阅"""
        stmt = select(PushSubscriptionModel).where(
            PushSubscriptionModel.id == subscription_id,
            PushSubscriptionModel.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_subscription_by_user_and_source(
        self, db: AsyncSession, *, user_id: int, source_id: int
    ) -> Optional[PushSubscriptionModel]:
        """检查用户是否已订阅特定来源"""
        stmt = select(PushSubscriptionModel).where(
            PushSubscriptionModel.user_id == user_id,
            PushSubscriptionModel.source_id == source_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_subscriptions_by_user_id(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100, only_active: bool = False
    ) -> List[PushSubscriptionModel]:
        """获取用户的所有订阅"""
        stmt = (
            select(PushSubscriptionModel)
            .where(PushSubscriptionModel.user_id == user_id)
            .order_by(PushSubscriptionModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if only_active:
            stmt = stmt.where(PushSubscriptionModel.is_active == True)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_subscribers_for_source( # 用于消息分发
        self, db: AsyncSession, *, source_id: int, only_active_subscriptions: bool = True, only_active_users: bool = True
    ) -> List[UserModel]: # 返回订阅了该来源的用户列表
        """获取订阅了特定来源的活跃用户列表"""
        stmt = select(UserModel).join(PushSubscriptionModel, UserModel.id == PushSubscriptionModel.user_id)
        conditions = [PushSubscriptionModel.source_id == source_id]
        if only_active_subscriptions:
            conditions.append(PushSubscriptionModel.is_active == True)
        if only_active_users:
            conditions.append(UserModel.is_active == True) # 确保用户账户也激活

        stmt = stmt.where(and_(*conditions))
        result = await db.execute(stmt)
        return result.scalars().unique().all() # .unique() 确保每个用户只返回一次

    async def create_subscription(
        self, db: AsyncSession, *, obj_in: PushSubscriptionCreate, user_id: int
    ) -> PushSubscriptionModel:
        """创建用户订阅"""
        # 检查是否已订阅 (UniqueConstraint 也会在数据库层面阻止，但最好在应用层面也检查)
        existing_subscription = await self.get_subscription_by_user_and_source(
            db, user_id=user_id, source_id=obj_in.source_id
        )
        if existing_subscription:
            # 可以选择更新现有订阅的状态，或者直接返回错误/现有订阅
            # 这里我们假设如果已存在则不重复创建 (或由API端点处理此逻辑)
            raise ValueError("User is already subscribed to this source.") # 或者返回现有订阅

        db_obj_data = obj_in.model_dump()
        db_obj_data["user_id"] = user_id
        db_obj = PushSubscriptionModel(**db_obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_subscription(
        self, db: AsyncSession, *, db_obj: PushSubscriptionModel, obj_in: Union[PushSubscriptionUpdate, Dict[str, Any]]
    ) -> PushSubscriptionModel:
        """更新用户订阅 (通常是 is_active 或 user_specific_config)"""
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

    async def remove_subscription(
        self, db: AsyncSession, *, subscription_id: int, user_id: int
    ) -> Optional[PushSubscriptionModel]:
        """用户取消订阅 (删除订阅记录)"""
        subscription_to_delete = await self.get_subscription_by_id(db, subscription_id=subscription_id, user_id=user_id)
        if subscription_to_delete:
            await db.delete(subscription_to_delete)
            await db.commit()
        return subscription_to_delete

# --- CRUD for PushMessage (消息的创建、读取、状态更新) ---
class CRUDPushMessage:
    async def get_message_by_id(
        self, db: AsyncSession, *, message_id: int, user_id: Optional[int] = None # 如果提供了 user_id，则验证消息是否属于该用户
    ) -> Optional[PushMessageModel]:
        stmt = select(PushMessageModel).where(PushMessageModel.id == message_id)
        if user_id is not None:
            stmt = stmt.where(PushMessageModel.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_messages_for_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        source_id: Optional[int] = None, # 按来源筛选
        status: Optional[str] = None,    # 按状态筛选
        unread_only: Optional[bool] = None # 仅未读
    ) -> List[PushMessageModel]:
        """获取指定用户收到的消息列表，支持筛选和分页"""
        stmt = select(PushMessageModel).where(PushMessageModel.user_id == user_id)
        if source_id is not None:
            stmt = stmt.where(PushMessageModel.source_id == source_id)
        if status is not None:
            stmt = stmt.where(PushMessageModel.status == status)
        if unread_only is True: # 明确检查 True，因为 None 和 False 行为不同
            stmt = stmt.where(PushMessageModel.status == "unread") # 假设 "unread" 是未读状态

        stmt = stmt.order_by(PushMessageModel.received_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_message_for_user( # 单条消息创建
        self,
        db: AsyncSession,
        *,
        user_id: int,
        source_id: int,
        title: Optional[str],
        content: str,
        content_type: str = "text/plain",
        raw_data: Optional[Dict[str, Any]] = None,
        status: str = "unread" # 初始状态
    ) -> PushMessageModel:
        """为特定用户创建一条推送消息记录"""
        db_obj = PushMessageModel(
            user_id=user_id,
            source_id=source_id,
            title=title,
            content=content,
            content_type=content_type,
            raw_data=raw_data,
            status=status,
            # received_at, created_at, updated_at 会有默认值
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_messages_for_subscribers( # 批量消息创建 (核心)
        self,
        db: AsyncSession,
        *,
        source_id: int, # 消息来自哪个源
        title: Optional[str],
        content: str,
        content_type: str = "text/plain",
        raw_data: Optional[Dict[str, Any]] = None
        # status 默认为 unread
    ) -> List[PushMessageModel]:
        """
        当一个 PushSource 接收到新内容时，为所有订阅了该来源的活跃用户创建消息。
        这是消息分发的核心逻辑。
        """
        subscribers = await crud_push_subscription.get_subscribers_for_source(
            db, source_id=source_id, only_active_subscriptions=True, only_active_users=True
        )
        if not subscribers:
            return []

        new_messages: List[PushMessageModel] = []
        for user in subscribers:
            # 这里可以添加更复杂的逻辑，例如检查用户是否已接收过类似消息 (去重)
            # 或者根据用户的 user_specific_config 定制消息内容 (如果适用)
            db_message = PushMessageModel(
                user_id=user.id,
                source_id=source_id,
                title=title,
                content=content,
                content_type=content_type,
                raw_data=raw_data,
                status="unread",
            )
            db.add(db_message) # 先添加所有，最后一次性提交
            new_messages.append(db_message)

        if new_messages:
            await db.commit()
            for msg in new_messages: # 刷新每个新创建的消息以获取ID等
                await db.refresh(msg)
        return new_messages

    async def update_message_status(
        self, db: AsyncSession, *, message_id: int, user_id: int, new_status: str
    ) -> Optional[PushMessageModel]:
        """更新用户特定消息的状态 (例如，标记为已读)"""
        message = await self.get_message_by_id(db, message_id=message_id, user_id=user_id)
        if not message:
            return None

        message.status = new_status
        if new_status == "read" and not message.read_at: # 如果标记为已读且之前未记录阅读时间
            from datetime import datetime, timezone
            message.read_at = datetime.now(timezone.utc)

        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    async def mark_all_messages_as_read_for_user(
        self, db: AsyncSession, *, user_id: int, source_id: Optional[int] = None
    ) -> int:
        """将用户（可选特定来源）的所有未读消息标记为已读，返回受影响的行数。"""
        from datetime import datetime, timezone
        current_time_utc = datetime.now(timezone.utc)

        conditions = [
            PushMessageModel.user_id == user_id,
            PushMessageModel.status == "unread"
        ]
        if source_id is not None:
            conditions.append(PushMessageModel.source_id == source_id)

        stmt = (
            sqlalchemy_update(PushMessageModel)
            .where(and_(*conditions))
            .values(status="read", read_at=current_time_utc, updated_at=current_time_utc) # 也更新 updated_at
            .execution_options(synchronize_session="fetch") # 或者 "evaluate"
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount # 返回更新的行数

    async def remove_message(self, db: AsyncSession, *, message_id: int, user_id: int) -> Optional[PushMessageModel]:
        """用户删除自己的某条消息 (逻辑删除或物理删除)"""
        # 这里实现物理删除，也可以改为更新状态为 "archived" 或 "deleted"
        message_to_delete = await self.get_message_by_id(db, message_id=message_id, user_id=user_id)
        if message_to_delete:
            await db.delete(message_to_delete)
            await db.commit()
        return message_to_delete

# 创建 CRUD 类的实例
crud_push_source = CRUDPushSource()
crud_push_subscription = CRUDPushSubscription()
crud_push_message = CRUDPushMessage()