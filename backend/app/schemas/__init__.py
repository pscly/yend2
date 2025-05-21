# backend/app/schemas/__init__.py (确保有这个文件，内容如下)
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserPublic,
    UserInternal,
    Token,
    TokenData, # <--- 确保 TokenData 被导出 (或可以直接从 app.schemas.user 导入)
    PasswordResetRequest,
    PasswordResetConfirm
)
from .navigation import (
    NavigationItemBase,
    NavigationItemCreate,
    NavigationItemUpdate,
    NavigationItemPublic,
    NavigationGroupBase,
    NavigationGroupCreate,
    NavigationGroupUpdate,
    NavigationGroupPublic,
    NavigationGroupWithItemsPublic,
)
from .push import (
    PushSourceBase,
    PushSourceCreate,
    PushSourceUpdate,
    PushSourcePublic,
    PushSubscriptionBase,
    PushSubscriptionCreate,
    PushSubscriptionUpdate,
    PushSubscriptionPublic,
    WebhookMessagePayload,
    PushMessageUpdate,
    PushMessagePublic,
)