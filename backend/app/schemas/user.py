# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid # 如果你的 User 模型使用 UUID作为 id

# --- 基本 User Schema ---
class UserBase(BaseModel):
    """
    用户模型的基础 Schema，包含所有用户共有的、创建和更新时可能需要的字段。
    """
    username: str = Field(
        ..., # 表示该字段是必需的
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_]+$", # 示例：只允许字母、数字和下划线
        description="用户名，3-100个字符，只能包含字母、数字和下划线。"
    )
    email: Optional[EmailStr] = Field(
        None, # 表示该字段是可选的
        description="用户的电子邮箱，必须是有效的邮箱格式。"
    )
    is_active: Optional[bool] = Field(
        True,
        description="账户是否激活，默认为 True。"
    )
    is_superuser: bool = Field(
        False,
        description="是否为超级管理员，默认为 False。"
    )
    # is_verified: Optional[bool] = Field(False, description="邮箱是否已验证，默认为 False。") # 如果模型中有此字段

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid', # 不允许额外的字段
        # from_attributes=True # 如果需要从 ORM 对象创建 UserBase 实例
    )


# --- 用于创建用户的 Schema ---
class UserCreate(UserBase):
    """
    创建新用户时使用的 Schema。
    继承自 UserBase，并添加了密码字段。
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=128, # 适当限制最大长度
        description="用户密码，至少8个字符。"
    )


# --- 用于更新用户的 Schema ---
class UserUpdate(BaseModel):
    """
    更新用户信息时使用的 Schema。
    所有字段都是可选的，因为用户可能只更新部分信息。
    """
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="新的用户名。"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="新的电子邮箱。"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="新的用户密码（如果需要修改）。"
    )
    is_active: Optional[bool] = Field(
        None,
        description="更新账户激活状态。"
    )
    is_superuser: Optional[bool] = Field(
        None,
        description="更新用户是否为超级管理员。"
    )
    # is_verified: Optional[bool] = Field(None, description="更新邮箱验证状态。")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )


# --- 用于从数据库读取并返回给API客户端的 Schema (公共信息) ---
class UserPublic(UserBase): # 继承自 UserBase 以包含基本字段
    """
    公开的用户信息 Schema，用于 API 响应。
    不包含密码等敏感字段。
    """
    id: int # 或者 id: uuid.UUID，如果你的 User 模型使用 UUID
    # 如果 UserBase 中没有 is_active 和 is_superuser，则在这里添加
    # is_active: bool
    # is_superuser: bool
    created_at: datetime
    updated_at: datetime
    # last_login_at: Optional[datetime] = None # 如果模型中有此字段

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True, # 允许从 SQLAlchemy ORM 对象属性创建模型实例
        extra='ignore' # 对于从数据库读取的数据，可能有多余字段，选择忽略
    )


# --- 用于内部操作或包含敏感信息的 Schema (例如，从数据库读取完整用户对象) ---
class UserInternal(UserPublic): # 继承自 UserPublic
    """
    内部使用的用户 Schema，可能包含哈希密码等敏感信息。
    通常不在 API 响应中直接返回给客户端。
    """
    hashed_password: str

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )


# --- 用于 Token 相关的 Schemas ---
class Token(BaseModel):
    """
    JWT Token 响应 Schema。
    """
    access_token: str
    token_type: str = "bearer" # 通常固定为 "bearer"


class TokenPayload(BaseModel):
    """
    JWT Token 解码后的载荷数据 Schema。
    """
    sub: Optional[str] = None # "sub" (subject) 通常是用户名或用户ID
    user_id: Optional[int] = None # 或者 Optional[uuid.UUID]
    # exp: Optional[int] = None # 过期时间戳，通常由 JOSE 库处理
    # scopes: List[str] = [] # 如果你使用 OAuth2 scopes


# --- 用于请求新密码或重置密码的 Schema (可选) ---
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)