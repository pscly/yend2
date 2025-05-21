from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


# 新增：导入你的 Pydantic settings 和 SQLAlchemy Base
import os
import sys
from app.core.config import settings # 假设 settings 实例在这里
from app.db.base import Base       # 确保这个文件导入了所有模型
from sqlalchemy import engine_from_config, pool, create_engine 
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None
target_metadata = Base.metadata     # 更新

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    # 使用 settings 中的同步数据库 URL
    url = settings.SYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # 这里我们不使用 engine_from_config，而是直接用 settings.SYNC_DATABASE_URL 创建 engine
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}), # 原来的方式
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

    # 新的方式：使用 settings.SYNC_DATABASE_URL
    # 注意：Pydantic 的 DSN 类型可能需要转换为字符串
    db_url_str = str(settings.SYNC_DATABASE_URL)
    connectable = create_engine(db_url_str, poolclass=pool.NullPool) # 需要导入 create_engine from sqlalchemy

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # 可选：如果你的模型中使用了特定的 schema 名称
            # version_table_schema=target_metadata.schema,
            # include_schemas=True, # 如果你使用了多个 schema
        )

        with context.begin_transaction():
            context.run_migrations()
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
