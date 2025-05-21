# backend/app/models/push.py
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, Integer as SAInteger, String, DateTime, func, ForeignKey, Text, JSON, Boolean,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB # PostgreSQL 的 JSONB 类型性能更好

from app.db.base_class import Base
from app.models.user import User # 导入 User 模型以建立关系

# --- 推送来源模型 ---
class PushSource(Base):
    """
    推送来源模型 (SQLAlchemy Table)
    例如：某个钉钉机器人、某个微信公众号API、自定义Webhook等。
    通常由管理员配置。
    """
    __tablename__ = "push_sources"

    id = Column(SAInteger, primary_key=True, index=True, autoincrement=True, comment="推送来源ID")
    # id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, unique=True, comment="推送来源UUID")

    name = Column(String(100), nullable=False, unique=True, index=True, comment="推送来源的易记名称")
    source_type = Column(String(50), nullable=False, index=True, comment="来源类型 (如 'dingtalk', 'wechat_mp', 'webhook', 'email')")
    # config 字段存储特定来源的配置信息，如 webhook_url, app_id, secret等。
    # 注意：存储敏感信息 (如 API Secret) 时应考虑加密或使用 secrets manager。
    # 使用 JSONB (PostgreSQL) 或 JSON (其他数据库)。
    # config = Column(JSONB if Base.metadata.bind and 'postgresql' in Base.metadata.bind.dialect.name else JSON,
                    # nullable=True, comment="来源的特定配置 (JSON格式)")

    config = Column(JSON, nullable=True, comment="来源的特定配置 (JSON格式)")
    description = Column(Text, nullable=True, comment="推送来源的描述 (可选)")
    is_active = Column(Boolean, default=True, nullable=False, comment="此推送来源是否启用")
    # identifier = Column(String(100), unique=True, index=True, nullable=True, comment="用于Webhook的唯一标识符 (可选)") # 如果需要一个易于URL的标识符

    # --- 时间戳 ---
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="最后更新时间")

    # --- 关系 (Relationships) ---
    # 一个推送来源可以被多个用户订阅
    subscriptions = relationship(
        "PushSubscription",
        back_populates="source",
        cascade="all, delete-orphan", # 如果删除来源，相关的订阅也删除
        lazy="selectin"
    )

    # 从此来源发出的所有消息 (如果需要双向关联)
    messages_originated = relationship(
        "PushMessage",
        back_populates="source_of_message", # 区分于 PushMessage 中的 user 关系
        cascade="all, delete-orphan", # 如果删除来源，相关的消息也删除 (谨慎)
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<PushSource(id={self.id}, name='{self.name}', type='{self.source_type}')>"


# --- 用户推送订阅模型 ---
class PushSubscription(Base):
    """
    用户对推送来源的订阅关系模型 (SQLAlchemy Table)
    """
    __tablename__ = "push_subscriptions"

    id = Column(SAInteger, primary_key=True, index=True, autoincrement=True, comment="订阅关系ID")
    # id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, unique=True, comment="订阅关系UUID")

    # --- 外键关联 ---
    user_id = Column(SAInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="订阅用户ID")
    # user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="订阅用户UUID")

    source_id = Column(SAInteger, ForeignKey("push_sources.id", ondelete="CASCADE"), nullable=False, index=True, comment="订阅的推送来源ID")
    # source_id = Column(PG_UUID(as_uuid=True), ForeignKey("push_sources.id", ondelete="CASCADE"), nullable=False, index=True, comment="订阅的推送来源UUID")

    # 用户针对此订阅的特定配置 (可选)
    # 例如，如果来源是“通用邮件推送”，这里可以存用户的目标邮箱地址
    # 如果来源是某个需要用户提供特定参数的Webhook，也可以存在这里
    # user_specific_config = Column(JSONB if Base.metadata.bind and 'postgresql' in Base.metadata.bind.dialect.name else JSON,
    #                               nullable=True, comment="用户针对此订阅的特定配置 (JSON格式)")
    config = Column(JSON, nullable=True, comment="来源的特定配置 (JSON格式)")

    is_active = Column(Boolean, default=True, nullable=False, comment="用户是否希望接收此订阅的推送")

    # --- 时间戳 ---
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="订阅创建时间")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="订阅最后更新时间")

    # --- 关系 (Relationships) ---
    user = relationship("User", back_populates="push_subscriptions")
    source = relationship("PushSource", back_populates="subscriptions")

    # --- 约束 ---
    # 确保一个用户对一个推送来源只能有一个订阅记录
    __table_args__ = (
        UniqueConstraint('user_id', 'source_id', name='uq_user_source_subscription'),
    )

    def __repr__(self) -> str:
        return f"<PushSubscription(id={self.id}, user_id={self.user_id}, source_id={self.source_id}, active={self.is_active})>"


# --- 推送消息模型 ---
class PushMessage(Base):
    """
    存储的推送消息模型 (SQLAlchemy Table)
    这是发送给特定用户的具体消息记录。
    """
    __tablename__ = "push_messages"

    id = Column(SAInteger, primary_key=True, index=True, autoincrement=True, comment="消息ID")
    # id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, unique=True, comment="消息UUID")

    # --- 消息归属 ---
    # 消息的目标用户
    user_id = Column(SAInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="接收消息的用户ID (如果用户被删除，消息可保留)")
    # user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="接收消息的用户UUID")

    # 消息的原始来源
    source_id = Column(SAInteger, ForeignKey("push_sources.id", ondelete="SET NULL"), nullable=True, index=True, comment="消息的原始来源ID (如果来源被删除，消息可保留)")
    # source_id = Column(PG_UUID(as_uuid=True), ForeignKey("push_sources.id", ondelete="SET NULL"), nullable=True, index=True, comment="消息的原始来源UUID")

    # --- 消息内容 ---
    title = Column(String(255), nullable=True, comment="消息标题 (可选)")
    content = Column(Text, nullable=False, comment="消息主体内容 (可以是纯文本、Markdown、HTML片段等)")
    content_type = Column(String(50), default="text/plain", nullable=False, comment="内容类型 (如 'text/plain', 'text/markdown', 'application/json')")
    # 原始推送数据，用于调试、未来扩展或重新处理
    # raw_data = Column(JSONB if Base.metadata.bind and 'postgresql' in Base.metadata.bind.dialect.name else JSON,
    #                   nullable=True, comment="从来源接收到的原始数据 (JSON格式)")
    config = Column(JSON, nullable=True, comment="来源的特定配置 (JSON格式)")


    # --- 消息状态与时间 ---
    status = Column(String(50), default="unread", nullable=False, index=True, comment="消息状态 (如 'unread', 'read', 'archived', 'failed_to_send')")
    # 系统收到来自外部来源消息的时间
    received_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True, comment="系统接收到消息的时间")
    # 如果系统还负责将此消息转发给用户的其他客户端 (如邮件、App通知)，则为实际发送时间
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="消息实际发送给用户终端的时间 (可选)")
    # 用户阅读消息的时间
    read_at = Column(DateTime(timezone=True), nullable=True, comment="用户阅读消息的时间 (可选)")

    # --- 时间戳 ---
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="记录创建时间")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="记录最后更新时间")

    # --- 关系 (Relationships) ---
    # 关联到接收消息的用户
    user = relationship("User", back_populates="push_messages_received")
    # 关联到消息的原始来源
    source_of_message = relationship("PushSource", back_populates="messages_originated") # 重命名以避免与 PushSource.subscriptions 中的 source 冲突

    def __repr__(self) -> str:
        return f"<PushMessage(id={self.id}, user_id={self.user_id}, source_id={self.source_id}, status='{self.status}')>"