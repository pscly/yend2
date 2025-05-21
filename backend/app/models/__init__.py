# backend/app/models/__init__.py

# 导入所有 SQLAlchemy 模型，以便 Base 可以发现它们，
# 并且其他模块可以方便地从 app.models 导入。

from .user import User  # noqa: F401 (告诉 linter 导入是故意未使用的)
from .navigation import NavigationGroup, NavigationItem  # noqa <--- 新增这行
from .push import PushSource, PushSubscription, PushMessage  

# 如果你还有其他模型文件，也在这里导入
# from .another_model import AnotherModel # noqa: F401