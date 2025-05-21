# backend/app/models/user.py
import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # 使用 PostgreSQL 原生 UUID 类型

from app.db.base_class import Base # 导入你定义的声明式基类

class User(Base):
    """
    用户模型 (SQLAlchemy Table)
    """
    __tablename__ = "users" # 明确指定表名，可以覆盖 Base 中的自动生成规则

    # --- 主键 ---
    # 方案一: 使用自增整数 ID (简单，常见)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 方案二: 使用 UUID作为主键 (更适合分布式系统，ID不易被猜测)
    # 如果选择 UUID，请取消注释下面这行，并注释掉上面的 Integer ID
    # id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, unique=True)
    # 注意：如果使用 UUID，外键也需要对应修改。为了简单起见，我们这里先用 Integer ID。

    # --- 核心字段 ---
    username = Column(String(100), unique=True, index=True, nullable=False, comment="用户名，唯一")
    email = Column(String(255), unique=True, index=True, nullable=True, comment="电子邮箱，唯一，可选") # 邮箱可用于找回密码等
    hashed_password = Column(String(255), nullable=False, comment="哈希后的密码")

    # --- 状态与权限 ---
    is_active = Column(Boolean(), default=True, nullable=False, comment="账户是否激活")
    is_superuser = Column(Boolean(), default=False, nullable=False, comment="是否为超级管理员")
    # is_verified = Column(Boolean(), default=False, nullable=False, comment="邮箱是否已验证") # 可选

    # --- 时间戳 ---
    # default=func.now() 使用数据库服务器的当前时间
    # onupdate=func.now() 在更新时自动更新时间戳
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="创建时间 (带时区)")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="最后更新时间 (带时区)")
    # last_login_at = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间") # 可选

    # --- 关系 (Relationships) ---
    # 一个用户可以有多个导航分组
    # cascade="all, delete-orphan": 当 User 被删除时，其关联的 navigation_groups 也会被删除。
    # lazy="selectin": 推荐的加载策略之一，避免 N+1 问题。
    navigation_groups = relationship(
        "NavigationGroup",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin" # 或者 "joined", "subquery"
    )

    # 一个用户可以有多个推送订阅
    push_subscriptions = relationship(
        "PushSubscription",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # 一个用户可以接收多个推送消息 (如果消息与用户强绑定，并且删除用户时也删除其消息)
    # 如果消息是独立的，或者你希望保留用户的历史消息，这里的 cascade 行为可能不同
    push_messages_received = relationship(
        "PushMessage",
        back_populates="user", # 假设 PushMessage 模型中有个 user 关系指向 User
        cascade="all, delete-orphan", # 谨慎使用，如果删除用户也删除其所有消息
        lazy="selectin"
    )

    # --- 魔术方法 ---
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    # --- 属性 (可选的 Python 属性，不直接映射到数据库列) ---
    # @property
    # def full_name(self) -> str:
    #     # 假设你有 first_name 和 last_name 字段
    #     if self.first_name and self.last_name:
    #         return f"{self.first_name} {self.last_name}"
    #     return self.username