# backend/app/db/base.py

# 这个文件用于确保 SQLAlchemy Base 类和所有模型都被加载，
# 以便 Alembic 可以检测到模型的元数据。

# 导入 Base 类 (所有模型都继承自它)
from app.db.base_class import Base  # noqa: F401

# 导入 app.models 包，这将执行 app/models/__init__.py，
# 从而加载其中定义的所有模型。
import app.models  # noqa: F401
