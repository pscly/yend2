# backend/app/models/navigation.py
import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Integer as SAInteger # 重命名 Integer 以避免与 Python 内置冲突
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.base_class import Base
from app.models.user import User # 导入 User 模型以建立关系

class NavigationGroup(Base):
    """
    导航分组模型 (SQLAlchemy Table)
    用于用户组织其导航链接。
    """
    __tablename__ = "navigation_groups"

    id = Column(SAInteger, primary_key=True, index=True, autoincrement=True, comment="导航分组ID")
    # id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, unique=True, comment="导航分组UUID") # 如果选择 UUID

    name = Column(String(100), nullable=False, index=True, comment="导航分组名称")
    description = Column(Text, nullable=True, comment="导航分组描述 (可选)")
    order_index = Column(SAInteger, default=0, nullable=False, comment="用于用户自定义排序的索引") # 排序字段

    # --- 外键关联到 User 模型 ---
    user_id = Column(SAInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属用户ID")
    # user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属用户UUID") # 如果 User 模型使用 UUID

    # --- 时间戳 ---
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="最后更新时间")

    # --- 关系 (Relationships) ---
    # 反向关联到 User 模型
    owner = relationship("User", back_populates="navigation_groups")

    # 一个导航分组可以包含多个导航项
    # cascade="all, delete-orphan": 当 NavigationGroup 被删除时，其关联的 items 也会被删除。
    # order_by="NavigationItem.order_index": 获取 items 时默认按 order_index 排序。
    items = relationship(
        "NavigationItem",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin", # 推荐的加载策略
        order_by="NavigationItem.order_index" # 确保获取时有序
    )

    def __repr__(self) -> str:
        return f"<NavigationGroup(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class NavigationItem(Base):
    """
    导航项模型 (SQLAlchemy Table)
    代表一个具体的链接。
    """
    __tablename__ = "navigation_items"

    id = Column(SAInteger, primary_key=True, index=True, autoincrement=True, comment="导航项ID")
    # id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, unique=True, comment="导航项UUID") # 如果选择 UUID

    title = Column(String(200), nullable=False, comment="导航项标题")
    url = Column(String(2083), nullable=False, comment="导航项链接 URL (URL RFC 推荐最大长度)") # 2083 是 IE 的限制，通常够用
    icon_url = Column(String(2083), nullable=True, comment="导航项图标的 URL (可选)")
    description = Column(Text, nullable=True, comment="导航项描述 (可选)")
    order_index = Column(SAInteger, default=0, nullable=False, comment="组内排序索引") # 排序字段

    # --- 外键关联到 NavigationGroup 模型 ---
    group_id = Column(SAInteger, ForeignKey("navigation_groups.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属导航分组ID")
    # group_id = Column(PG_UUID(as_uuid=True), ForeignKey("navigation_groups.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属导航分组UUID") # 如果 NavigationGroup 使用 UUID

    # --- 时间戳 ---
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="最后更新时间")

    # --- 关系 (Relationships) ---
    # 反向关联到 NavigationGroup 模型
    group = relationship("NavigationGroup", back_populates="items")

    def __repr__(self) -> str:
        return f"<NavigationItem(id={self.id}, title='{self.title}', group_id={self.group_id})>"