# backend/app/schemas/navigation.py
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

# --- NavigationItem Schemas ---
class NavigationItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="导航项标题")
    url: HttpUrl = Field(..., description="导航项的有效链接 URL")
    icon_url: Optional[HttpUrl] = Field(None, description="导航项图标的 URL (可选)")
    description: Optional[str] = Field(None, max_length=500, description="导航项描述 (可选)")
    order_index: int = Field(default=0, description="组内排序索引，默认为0")
    model_config = ConfigDict(extra='forbid')

class NavigationItemCreate(NavigationItemBase):
    pass

class NavigationItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[HttpUrl] = Field(None)
    icon_url: Optional[HttpUrl] = Field(None)
    description: Optional[str] = Field(None, max_length=500)
    order_index: Optional[int] = Field(None)
    model_config = ConfigDict(extra='forbid')

class NavigationItemPublic(NavigationItemBase):
    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True, extra='ignore')

# --- NavigationGroup Schemas ---
class NavigationGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="导航分组名称")
    description: Optional[str] = Field(None, max_length=500, description="导航分组描述 (可选)")
    order_index: int = Field(default=0, description="排序索引，默认为0")
    model_config = ConfigDict(extra='forbid')

class NavigationGroupCreate(NavigationGroupBase):
    pass

class NavigationGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    order_index: Optional[int] = Field(None)
    model_config = ConfigDict(extra='forbid')

class NavigationGroupPublic(NavigationGroupBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True, extra='ignore')

class NavigationGroupWithItemsPublic(NavigationGroupPublic):
    items: List[NavigationItemPublic] = Field(default_factory=list) # 使用 default_factory
    model_config = ConfigDict(from_attributes=True, extra='ignore')