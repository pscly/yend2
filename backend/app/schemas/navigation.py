# backend/app/schemas/navigation.py
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid # 如果你的模型使用 UUID 作为 id

# --- NavigationItem Schemas ---

class NavigationItemBase(BaseModel):
    """
    导航项的基础 Schema。
    """
    title: str = Field(..., min_length=1, max_length=200, description="导航项标题")
    url: HttpUrl = Field(..., description="导航项的有效链接 URL") # HttpUrl 会验证 URL 格式
    icon_url: Optional[HttpUrl] = Field(None, description="导航项图标的 URL (可选)")
    description: Optional[str] = Field(None, max_length=500, description="导航项描述 (可选)")
    order_index: int = Field(default=0, description="组内排序索引，默认为0")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class NavigationItemCreate(NavigationItemBase):
    """
    创建新导航项时使用的 Schema。
    通常需要指定所属的分组ID。
    """
    # group_id 在 API 端点层面处理或作为路径参数，通常不直接放在创建 Schema 中，
    # 因为它依赖于上下文 (哪个分组下创建)。
    # 如果确实需要，可以添加：
    # group_id: int # 或者 uuid.UUID
    pass # 目前与 Base 相同，但保留以便未来扩展

class NavigationItemUpdate(BaseModel):
    """
    更新导航项时使用的 Schema。所有字段可选。
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="新的导航项标题")
    url: Optional[HttpUrl] = Field(None, description="新的导航项链接 URL")
    icon_url: Optional[HttpUrl] = Field(None, description="新的导航项图标 URL (设置为空字符串或null可清除)")
    description: Optional[str] = Field(None, max_length=500, description="新的导航项描述 (设置为空字符串或null可清除)")
    order_index: Optional[int] = Field(None, description="新的组内排序索引")
    # group_id: Optional[int] = None # 通常不允许直接修改所属分组，而是通过删除再创建或专门的移动接口

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class NavigationItemPublic(NavigationItemBase):
    """
    公开的导航项信息 Schema，用于 API 响应。
    """
    id: int # 或者 id: uuid.UUID
    group_id: int # 或者 group_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True, # 允许从 ORM 对象属性创建模型实例
        extra='ignore'
    )


# --- NavigationGroup Schemas ---

class NavigationGroupBase(BaseModel):
    """
    导航分组的基础 Schema。
    """
    name: str = Field(..., min_length=1, max_length=100, description="导航分组名称")
    description: Optional[str] = Field(None, max_length=500, description="导航分组描述 (可选)")
    order_index: int = Field(default=0, description="排序索引，默认为0")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class NavigationGroupCreate(NavigationGroupBase):
    """
    创建新导航分组时使用的 Schema。
    """
    # user_id 在 API 端点层面从当前登录用户获取，不通过请求体传入。
    pass # 目前与 Base 相同

class NavigationGroupUpdate(BaseModel):
    """
    更新导航分组时使用的 Schema。所有字段可选。
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="新的导航分组名称")
    description: Optional[str] = Field(None, max_length=500, description="新的导航分组描述 (设置为空字符串或null可清除)")
    order_index: Optional[int] = Field(None, description="新的排序索引")

    # Pydantic V2 配置
    model_config = ConfigDict(
        extra='forbid'
    )

class NavigationGroupPublic(NavigationGroupBase):
    """
    公开的导航分组信息 Schema，用于 API 响应。
    不直接包含导航项列表，以避免响应过大，导航项列表可以单独获取。
    """
    id: int # 或者 id: uuid.UUID
    user_id: int # 或者 user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )

class NavigationGroupWithItemsPublic(NavigationGroupPublic):
    """
    公开的导航分组信息 Schema，包含其下的导航项列表。
    用于需要一次性获取分组及其所有项的场景。
    """
    items: List[NavigationItemPublic] = [] # 默认为空列表

    # Pydantic V2 配置
    model_config = ConfigDict(
        from_attributes=True, # 确保 items 也能从 ORM 的 group.items 关系中填充
        extra='ignore'
    )