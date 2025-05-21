# backend/app/schemas/__init__.py

# 导入所有 Pydantic schemas，方便其他模块引用。

# --- User and Auth Schemas ---
# backend/app/schemas/__init__.py
from .user import ( # noqa
    UserBase,
    UserCreate,
    UserUpdate,
    UserPublic,
    UserInternal, # 如果你定义了这个
    Token,
    TokenPayload,
    PasswordResetRequest, # 如果你定义了这个
    PasswordResetConfirm  # 如果你定义了这个
)


from .navigation import ( # noqa <--- 新增这些行
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
from .push import ( # noqa <--- 新增这些行
    PushSourceBase,
    PushSourceCreate,
    PushSourceUpdate,
    PushSourcePublic,
    PushSubscriptionBase,
    PushSubscriptionCreate,
    PushSubscriptionUpdate,
    PushSubscriptionPublic,
    WebhookMessagePayload, # 如果你定义了这个
    PushMessageUpdate,
    PushMessagePublic,
)
# 如果你有其他模块的 schemas，也在这里导入
# from .other_schemas import OtherSchemaPublic # noqa: F401