# backend/app/crud/__init__.py

# 导入所有 CRUD 操作的实例或模块，方便服务层或 API 端点调用。

from .crud_user import user as crud_user  # 导出 user 实例并可以重命名
from .crud_navigation import ( # noqa <--- 新增这些行
    navigation_group as crud_navigation_group,
    navigation_item as crud_navigation_item,
)
from .crud_push import ( # noqa <--- 新增这些行
    crud_push_source,
    crud_push_subscription,
    crud_push_message,
)
# 如果你有其他模型的 CRUD 操作，也在这里导入
# from .crud_other import other_model as crud_other_model # noqa: F401