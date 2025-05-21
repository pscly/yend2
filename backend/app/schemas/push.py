# backend/app/schemas/push.py
from pydantic import BaseModel, Field, ConfigDict, computed_field # 确保导入 computed_field
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
    # 数据库中为 JSON 类型，Pydantic 中通常映射为 Dict 或 List
    config: Optional[Dict[str, Any]] = Field(None, description="来源的特定配置 (JSON对象)，例如 webhook URL、API 密钥等")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushSourceCreate(PushSourceBase):
    """
    创建新推送来源时使用的 Schema。
    """
    pass

class PushSourceUpdate(BaseModel):
    """
    更新推送来源时使用的 Schema。所有字段可选。
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)
    config: Optional[Dict[str, Any]] = Field(None, description="更新来源的特定配置 (JSON对象)")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushSourcePublic(PushSourceBase):
    """
    公开的推送来源信息 Schema，用于 API 响应。
    原始 config 字段将被排除，通过 config_display 提供处理过的版本。
    """
    id: int # 或者 id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # 使用 computed_field 来创建一个序列化时计算的字段 config_display
    # 它会替代原始的 config 字段在序列化输出中的位置（如果原始 config 被排除了）
    @computed_field(return_type=Optional[Dict[str, Any]])
    @property
    def config_display(self) -> Optional[Dict[str, Any]]:
        """
        提供一个用于显示的、可能经过处理的配置版本。
        这里可以实现逻辑来过滤掉敏感信息。
        """
        if self.config: # self.config 是从 PushSourceBase 继承来的
            # 示例：只返回非敏感部分，例如只返回 webhook_url (如果存在)
            # 实际逻辑取决于你的 config 结构和安全需求
            safe_config = {}
            if "webhook_url" in self.config: # 假设 self.config 是一个字典
                safe_config["webhook_url"] = self.config.get("webhook_url")
            # 你可以添加其他你想公开的配置项
            # 如果没有可公开的，或者你不想公开任何配置，可以返回 None 或空字典
            return safe_config # 或者 return {} 或 return None
        return None

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True, # 允许从 ORM 对象属性创建模型实例
        extra='ignore',
        # 通过 fields 配置来排除原始的 config 字段的序列化
        fields={
            "config": {"exclude": True} # 在序列化时排除原始的 config 字段
        }
    )


# --- PushSubscription Schemas ---

class PushSubscriptionBase(BaseModel):
    """
    用户推送订阅的基础 Schema。
    """
    is_active: bool = Field(True, description="用户是否希望接收此订阅的推送，默认为 True")
    user_specific_config: Optional[Dict[str, Any]] = Field(None, description="用户针对此订阅的特定配置 (JSON对象)")

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
    user_specific_config: Optional[Dict[str, Any]] = Field(None)

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
    source: Optional[PushSourcePublic] = None # (可选) 嵌套返回订阅的来源信息 (已处理config)

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

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class WebhookMessagePayload(BaseModel):
    """
    用于接收外部 Webhook 消息的 Schema。
    """
    source_identifier: str # 用于识别是哪个 PushSource
    title: Optional[str] = None
    content: str
    content_type: Optional[str] = "text/plain"
    # Webhook 可能还包含其他特定于来源的字段
    extra_data: Optional[Dict[str, Any]] = None # 用于存储原始payload中其他字段

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
    user_id: Optional[int] = None
    source_id: Optional[int] = None
    status: str
    received_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # raw_data 字段通常不返回给客户端，如果需要，可以像 config 一样处理
    # raw_data_display: Optional[Any] = None
    source: Optional[PushSourcePublic] = None # (可选) 嵌套返回消息的来源信息 (已处理config)

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
        # 如果需要处理 raw_data 的序列化:
        # fields={"raw_data": {"exclude": True}} # 假设原始 raw_data 字段在 PushMessageBase 或其父类中
    )
    # 如果 PushMessageBase 没有 raw_data，但 ORM 模型有，且你想在这里控制
    # @computed_field(...)
    # @property
    # def raw_data_display(self): ...# backend/app/schemas/push.py
from pydantic import BaseModel, Field, ConfigDict, computed_field # 确保导入 computed_field
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
    # 数据库中为 JSON 类型，Pydantic 中通常映射为 Dict 或 List
    config: Optional[Dict[str, Any]] = Field(None, description="来源的特定配置 (JSON对象)，例如 webhook URL、API 密钥等")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushSourceCreate(PushSourceBase):
    """
    创建新推送来源时使用的 Schema。
    """
    pass

class PushSourceUpdate(BaseModel):
    """
    更新推送来源时使用的 Schema。所有字段可选。
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)
    config: Optional[Dict[str, Any]] = Field(None, description="更新来源的特定配置 (JSON对象)")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class PushSourcePublic(PushSourceBase):
    """
    公开的推送来源信息 Schema，用于 API 响应。
    原始 config 字段将被排除，通过 config_display 提供处理过的版本。
    """
    id: int # 或者 id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # 使用 computed_field 来创建一个序列化时计算的字段 config_display
    # 它会替代原始的 config 字段在序列化输出中的位置（如果原始 config 被排除了）
    @computed_field(return_type=Optional[Dict[str, Any]])
    @property
    def config_display(self) -> Optional[Dict[str, Any]]:
        """
        提供一个用于显示的、可能经过处理的配置版本。
        这里可以实现逻辑来过滤掉敏感信息。
        """
        if self.config: # self.config 是从 PushSourceBase 继承来的
            # 示例：只返回非敏感部分，例如只返回 webhook_url (如果存在)
            # 实际逻辑取决于你的 config 结构和安全需求
            safe_config = {}
            if "webhook_url" in self.config: # 假设 self.config 是一个字典
                safe_config["webhook_url"] = self.config.get("webhook_url")
            # 你可以添加其他你想公开的配置项
            # 如果没有可公开的，或者你不想公开任何配置，可以返回 None 或空字典
            return safe_config # 或者 return {} 或 return None
        return None

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True, # 允许从 ORM 对象属性创建模型实例
        extra='ignore',
        # 通过 fields 配置来排除原始的 config 字段的序列化
        fields={
            "config": {"exclude": True} # 在序列化时排除原始的 config 字段
        }
    )


# --- PushSubscription Schemas ---

class PushSubscriptionBase(BaseModel):
    """
    用户推送订阅的基础 Schema。
    """
    is_active: bool = Field(True, description="用户是否希望接收此订阅的推送，默认为 True")
    user_specific_config: Optional[Dict[str, Any]] = Field(None, description="用户针对此订阅的特定配置 (JSON对象)")

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
    user_specific_config: Optional[Dict[str, Any]] = Field(None)

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
    source: Optional[PushSourcePublic] = None # (可选) 嵌套返回订阅的来源信息 (已处理config)

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

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class WebhookMessagePayload(BaseModel):
    """
    用于接收外部 Webhook 消息的 Schema。
    """
    source_identifier: str # 用于识别是哪个 PushSource
    title: Optional[str] = None
    content: str
    content_type: Optional[str] = "text/plain"
    # Webhook 可能还包含其他特定于来源的字段
    extra_data: Optional[Dict[str, Any]] = None # 用于存储原始payload中其他字段

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
    user_id: Optional[int] = None
    source_id: Optional[int] = None
    status: str
    received_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # raw_data 字段通常不返回给客户端，如果需要，可以像 config 一样处理
    # raw_data_display: Optional[Any] = None
    source: Optional[PushSourcePublic] = None # (可选) 嵌套返回消息的来源信息 (已处理config)

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
        # 如果需要处理 raw_data 的序列化:
        # fields={"raw_data": {"exclude": True}} # 假设原始 raw_data 字段在 PushMessageBase 或其父类中
    )
    # 如果 PushMessageBase 没有 raw_data，但 ORM 模型有，且你想在这里控制
    # @computed_field(...)
    # @property
    # def raw_data_display(self): ...