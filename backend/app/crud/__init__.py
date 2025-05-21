# backend/app/crud/__init__.py

from .crud_user import user as crud_user  # noqa: F401
from .crud_navigation import (  # noqa: F401
    crud_navigation_group, # 直接导出实例
    crud_navigation_item   # 直接导出实例
)
from .crud_push import (  # noqa: F401
    crud_push_source,
    crud_push_subscription,
    crud_push_message,
)

# 如果你有其他模型的 CRUD 操作，也在这里导入
# from .crud_other import other_model as crud_other_model # noqa: F401