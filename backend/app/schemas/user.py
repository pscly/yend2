# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict # Pydantic V2 ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid # 如果你的 User 模型使用 UUID 作为 id

# --- 基本 User Schema ---
class UserBase(BaseModel):
    """
    用户模型的基础 Schema，包含所有用户共有的、创建和更新时可能需要的字段。
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="用户名，3-100个字符，只能包含字母、数字和下划线。"
    )
    email: Optional[EmailStr] = Field(
        None,
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

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid',
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
        max_length=128,
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

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )


# --- 用于从数据库读取并返回给API客户端的 Schema (公共信息) ---
class UserPublic(UserBase):
    """
    公开的用户信息 Schema，用于 API 响应。
    不包含密码等敏感字段。
    """
    id: int # 或者 id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )


# --- 用于内部操作或包含敏感信息的 Schema ---
class UserInternal(UserPublic):
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
    token_type: str = Field("bearer", description="Token 类型，通常为 'bearer'")


class TokenData(BaseModel): # <--- 这是关键的 TokenData 定义
    """
    JWT Token 解码后的载荷数据 Schema。
    """
    sub: Optional[str] = Field(None, description="Token 的主题 (通常是用户名)")
    user_id: Optional[int] = Field(None, description="用户ID (可选，如果包含在token中)") # 或者 Optional[uuid.UUID]


# --- 用于请求新密码或重置密码的 Schema (可选) ---
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str # 密码重置 token
    new_password: str = Field(..., min_length=8, max_length=128)