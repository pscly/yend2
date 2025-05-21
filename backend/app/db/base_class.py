# app/db/base_class.py

from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.dialects.postgresql import UUID # 仅当 PostgreSQL 是主要目标且想用原生 UUID
import uuid # 用于默认 UUID 值

# 注意：如果你不确定数据库类型，或者希望最大限度地兼容，
# 避免直接使用特定数据库的类型如 sqlalchemy.dialects.postgresql.UUID
# 可以考虑使用 String(36) 或 LargeBinary(16) 来存储 UUID。
# 但如果你的目标是 PostgreSQL，使用其原生 UUID 类型通常更好。

@as_declarative()
class Base:
    """
    基础模型类，所有 SQLAlchemy 模型都应从此类继承。
    它提供了自动的表名生成和一些可选的通用列。
    """
    id: Any  # 主要用于类型提示，让IDE知道所有模型都有id属性
    __name__: str

    # 自动生成表名
    # 例如：UserModel -> user_models (保持驼峰并加s)
    # 或者：User -> users (如果类名简单)
    # 你可以根据你的命名偏好调整此逻辑
    @declared_attr
    def __tablename__(cls) -> str:
        # 简单的将类名转为小写并加 's' 作为复数
        # 例如: User -> users, NavigationGroup -> navigationgroups
        # 对于一些不规则的复数，你可能需要在模型类中显式设置 __tablename__
        # 或者实现更复杂的复数转换逻辑
        name_parts = []
        current_word = ""
        for char in cls.__name__:
            if char.isupper() and current_word:
                name_parts.append(current_word.lower())
                current_word = char
            else:
                current_word += char
        if current_word:
            name_parts.append(current_word.lower())

        table_name = "_".join(name_parts)
        if not table_name.endswith("s"): # 简单的复数处理
            table_name += "s"
        return table_name

    # 可选：为所有表添加一个自增的整数主键（如果需要）
    # 如果你更倾向于在每个模型中单独定义主键（例如有时用UUID，有时用Integer），
    # 则可以注释掉或删除此部分。
    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 可选：为所有表添加 created_at 和 updated_at 时间戳列
    # 如果你希望这些列存在于所有表中，可以在这里定义。
    # 否则，在需要的模型中单独添加它们。
    # created_at = Column(DateTime, default=func.now(), nullable=False)
    # updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        # 提供一个通用的 __repr__ 方法，显示类名和主键
        # 假设所有模型都有一个名为 'id' 的主键属性
        pk = getattr(self, 'id', None)
        if pk is not None:
            return f"<{self.__class__.__name__}(id={pk})>"
        return f"<{self.__class__.__name__} (transient)>"

# --- 可选的 Mixin 类 ---
# 如果你有很多模型共享某些列或行为，可以使用 Mixin 类来避免代码重复。

class TimestampMixin:
    """
    一个 Mixin 类，用于向模型添加 `created_at` 和 `updated_at` 时间戳列。
    """
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class UUIDMixin:
    """
    一个 Mixin 类，用于向模型添加一个 UUID 类型的主键。
    主要用于 PostgreSQL。
    """
    # 如果你使用 PostgreSQL 并希望使用其原生的 UUID 类型
    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # 如果你需要更通用的 UUID 存储方式 (例如，作为字符串)
    # from sqlalchemy import String
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)


# 如何在模型中使用 Mixin:
# class YourModel(Base, TimestampMixin, UUIDMixin): # 继承顺序可能重要
#     __tablename__ = "your_models"
#     # ... 其他列 ...
#
#     # 如果 Base 中已经定义了 id，并且你也用了 UUIDMixin，
#     # 你可能需要在 YourModel 中覆盖 id 或者调整 Base 或 Mixin。
#     # 或者，Base 不定义通用 id，让 Mixin 或模型自身来定义。