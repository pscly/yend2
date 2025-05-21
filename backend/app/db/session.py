# backend/app/db/session.py
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # 如果使用异步

from app.core.config import settings

# 配置日志记录器
logger = logging.getLogger(__name__)

# --- 同步引擎和会话 ---
# 仅当你的 DATABASE_URL 是同步DSN时使用，或者用于 Alembic 等同步操作
# 假设 settings.SYNC_DATABASE_URL 是同步的 DSN
# 如果 SYNC_DATABASE_URL 为 None，你可能需要一个默认的同步 DSN 或在此处处理
sync_db_url = str(settings.SYNC_DATABASE_URL) if settings.SYNC_DATABASE_URL else str(settings.DATABASE_URL).replace("+asyncpg", "") # 简化的备用逻辑

# connect_args 仅对 SQLite 需要
connect_args = {}
if "sqlite" in sync_db_url:
    connect_args["check_same_thread"] = False

sync_engine = create_engine(
    sync_db_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


# --- 异步引擎和会话 (推荐用于 FastAPI) ---
# 仅当你的 DATABASE_URL 是异步DSN时使用 (例如 "postgresql+asyncpg://...")
if "asyncpg" in str(settings.DATABASE_URL) or "aiomysql" in str(settings.DATABASE_URL) or "aiosqlite" in str(settings.DATABASE_URL):
    async_engine = create_async_engine(
        str(settings.DATABASE_URL),
        pool_pre_ping=True,
        # echo=settings.DEBUG_MODE, # 可选：在调试模式下打印SQL语句
    )
    # 对于异步会话，我们需要使用不同的方式创建会话工厂
    AsyncSessionLocal = sessionmaker(
        class_=AsyncSession,
        expire_on_commit=False, # 推荐设置为 False 用于 FastAPI
        autocommit=False,
        autoflush=False,
    )
    # 然后设置引擎
    AsyncSessionLocal.configure(bind=async_engine)
else:
    # 如果 DATABASE_URL 不是异步的，可以不定义异步会话，或者抛出配置错误
    async_engine = None
    AsyncSessionLocal = None
    if settings.APP_ENV != "testing": # 测试环境可能不使用异步
        logger.warning(f"DATABASE_URL ('{settings.DATABASE_URL}') 不是已知的异步 DSN，异步数据库会话未配置。")

# 为了方便，我们可以导出一个通用的 SessionLocal，根据配置选择
# 但通常在 deps.py 中会更明确地选择使用哪个
# SessionLocal = AsyncSessionLocal if AsyncSessionLocal else SyncSessionLocal

# 验证数据库连接
try:
    if async_engine:
        # 异步连接测试需要在异步上下文中运行
        # 这里我们只记录日志，实际测试会在应用启动时进行
        logger.info("异步数据库引擎已配置，将在应用启动时测试连接。")
    if sync_engine:
        # 同步连接可以立即测试
        with sync_engine.connect() as connection:
            logger.info("同步数据库连接成功。")
except Exception as e:
    logger.error(f"数据库连接配置错误: {e}", exc_info=True)
    # 在生产环境中，可能需要更严格的错误处理
    if settings.APP_ENV == "production":
        raise