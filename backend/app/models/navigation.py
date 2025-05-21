# backend/app/models/navigation.py
import uuid
from datetime import datetime

from sqlalchemy import Column, Integer as SAInteger, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.base_class import Base
# from app.models.user import User # User 模型会在 User 类定义时被 SQLAlchemy 知道，这里通常不需要显式导入用于关系，除非类型提示需要

class NavigationGroup(Base):
    __tablename__ = "navigation_groups"

    id = Column(SAInteger, primary_key=True, index=True, autoincrement=True, comment="导航分组ID")
    name = Column(String(100), nullable=False, index=True, comment="导航分组名称")
    description = Column(Text, nullable=True, comment="导航分组描述 (可选)")
    order_index = Column(SAInteger, default=0, nullable=False, comment="用于用户自定义排序的索引")

    user_id = Column(SAInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属用户ID")

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="最后更新时间")

    owner = relationship("User", back_populates="navigation_groups") # User 是字符串，SQLAlchemy 会解析
    items = relationship(
        "NavigationItem", # NavigationItem 是字符串
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="NavigationItem.order_index" # NavigationItem.order_index 字符串
    )

    def __repr__(self) -> str:
        return f"<NavigationGroup(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class NavigationItem(Base):
    __tablename__ = "navigation_items"

    id = Column(SAInteger, primary_key=True, index=True, autoincrement=True, comment="导航项ID")
    title = Column(String(200), nullable=False, comment="导航项标题")
    url = Column(String(2083), nullable=False, comment="导航项链接 URL")
    icon_url = Column(String(2083), nullable=True, comment="导航项图标的 URL (可选)")
    description = Column(Text, nullable=True, comment="导航项描述 (可选)")
    order_index = Column(SAInteger, default=0, nullable=False, comment="组内排序索引")

    group_id = Column(SAInteger, ForeignKey("navigation_groups.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属导航分组ID")

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="最后更新时间")

    group = relationship("NavigationGroup", back_populates="items") # NavigationGroup 是字符串

    def __repr__(self) -> str:
        return f"<NavigationItem(id={self.id}, title='{self.title}', group_id={self.group_id})>"
