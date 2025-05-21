# backend/app/schemas/push.py
from pydantic import BaseModel, Field, ConfigDict, Json
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid # 如果你的模型使用 UUID 作为 id

# --- PushSource Schemas ---

class PushSourceBase(BaseModel):
    """
    推送来源的基础 Schema。
    """
    name: str = Field(..., min_length=1, max_length=100, description="推送来源的易记名称")
    source_type: str = Field(..., min_length=1, max_length=50, description="来源类型 (如 'dingtalk', 'webhook', 'email')")
    description: Optional[str] = Field(None, max_length=500, description="推送来源的描述 (可选)")
    is_active: bool = Field(True, description="此推送来源是否启用，默认为 True")
    # config 字段在创建和更新时可能需要更具体的类型，或者直接接受 JSON
    # 为了通用性，这里可以定义为 Json[Any] 或 Dict[str, Any]
    # 在 API 端点层面，可以根据 source_type 对 config 内容进行更细致的校验
    config: Optional[Json[Any]] = Field(None, description="来源的特定配置 (JSON格式)，例如 webhook URL、API 密钥等")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushSourceCreate(PushSourceBase):
    """
    创建新推送来源时使用的 Schema。
    """
    # 通常由管理员创建，所以不需要 user_id
    pass

class PushSourceUpdate(BaseModel):
    """
    更新推送来源时使用的 Schema。所有字段可选。
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = Field(None, min_length=1, max_length=50) # 通常来源类型创建后不应修改
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)
    config: Optional[Json[Any]] = Field(None, description="更新来源的特定配置 (JSON格式)")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushSourcePublic(PushSourceBase):
    """
    公开的推送来源信息 Schema，用于 API 响应。
    """
    id: int # 或者 id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # 敏感配置（如API Secret）不应在此公开 Schema 中返回
    # 如果需要返回部分配置，可以创建一个不含敏感信息的 config schema
    # config: Optional[Dict[str, Any]] = Field(None, description="来源的部分公开配置")

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )
    # 重写 config 字段以避免直接暴露敏感信息
    # (这是一种方式，另一种是在 CRUD 或 API层面处理)
    @Field(exclude=True) # 默认不序列化原始的 config
    def config_public(self) -> Optional[Dict[str, Any]]:
        # 示例：只返回 config 中的非敏感部分，或干脆不返回
        # if self.config and isinstance(self.config, dict):
        #     return {"webhook_url": self.config.get("webhook_url")} # 举例
        return None # 或者返回一个经过处理的、安全的配置版本


# --- PushSubscription Schemas ---

class PushSubscriptionBase(BaseModel):
    """
    用户推送订阅的基础 Schema。
    """
    # user_id 和 source_id 通常在创建时由 API 端点逻辑或路径参数提供
    is_active: bool = Field(True, description="用户是否希望接收此订阅的推送，默认为 True")
    user_specific_config: Optional[Json[Any]] = Field(None, description="用户针对此订阅的特定配置 (JSON格式)")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushSubscriptionCreate(PushSubscriptionBase):
    """
    用户创建新推送订阅时使用的 Schema。
    需要提供要订阅的 source_id。
    """
    source_id: int # 或者 source_id: uuid.UUID

class PushSubscriptionUpdate(BaseModel):
    """
    更新用户推送订阅时使用的 Schema。
    通常只允许更新 is_active 和 user_specific_config。
    """
    is_active: Optional[bool] = Field(None)
    user_specific_config: Optional[Json[Any]] = Field(None) # 允许用户更新他们的特定配置

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushSubscriptionPublic(PushSubscriptionBase):
    """
    公开的用户推送订阅信息 Schema，用于 API 响应。
    """
    id: int # 或者 id: uuid.UUID
    user_id: int # 或者 user_id: uuid.UUID
    source_id: int # 或者 source_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    source: Optional[PushSourcePublic] = None # (可选) 嵌套返回订阅的来源信息

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )


# --- PushMessage Schemas ---

class PushMessageBase(BaseModel):
    """
    推送消息的基础 Schema。
    """
    title: Optional[str] = Field(None, max_length=255, description="消息标题 (可选)")
    content: str = Field(..., description="消息主体内容")
    content_type: str = Field("text/plain", max_length=50, description="内容类型 (如 'text/plain', 'text/markdown')")
    # raw_data 通常由系统内部记录，不通过 API 创建或更新时传入
    # status 通常由系统内部管理

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

# 创建 PushMessage 的 Schema 通常用于 Webhook 接收外部消息，其结构可能与 PushMessageBase 不同
# 例如，Webhook 可能会直接接收一个包含所有必要信息的 JSON 对象
class WebhookMessagePayload(BaseModel): # 示例：用于接收外部 Webhook 消息
    source_identifier: str # 用于识别是哪个 PushSource
    title: Optional[str] = None
    content: str
    content_type: Optional[str] = "text/plain"
    # Webhook 可能还包含其他特定于来源的字段
    extra_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='allow') # Webhook 可能包含未知字段

class PushMessageUpdate(BaseModel):
    """
    更新推送消息时使用的 Schema (例如，更新状态)。
    """
    status: Optional[str] = Field(None, max_length=50, description="消息状态 (如 'read', 'archived')")
    read_at: Optional[datetime] = Field(None, description="用户阅读消息的时间")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushMessagePublic(PushMessageBase):
    """
    公开的推送消息信息 Schema，用于 API 响应。
    """
    id: int # 或者 id: uuid.UUID
    user_id: Optional[int] = None # 或者 Optional[uuid.UUID], 因为可能 SET NULL
    source_id: Optional[int] = None # 或者 Optional[uuid.UUID], 因为可能 SET NULL
    status: str
    received_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # raw_data 通常不返回给客户端，除非有特定调试需求且已脱敏
    source: Optional[PushSourcePublic] = None # (可选) 嵌套返回消息的来源信息

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )