# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager # 用于 FastAPI 的 lifespan (替代 on_event)

from app.api.v1.router import api_router_v1
from app.core.config import settings
# from app.db import base # 确保所有模型被加载，主要用于 Alembic 或直接创建表
# from app.db.session import async_engine, sync_engine # 如果需要在 lifespan 中操作引擎

# --- Lifespan 事件处理器 (FastAPI 0.90.0+ 推荐方式) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 应用启动时执行 ---
    print(f"启动应用: {settings.PROJECT_NAME} v{settings.PROJECT_VERSION} (环境: {settings.APP_ENV})")
    # 示例: 检查数据库连接 (如果需要)
    # try:
    #     if async_engine:
    #         async with async_engine.connect() as connection:
    #             print("异步数据库连接成功。")
    #     if sync_engine:
    #         with sync_engine.connect() as connection:
    #             print("同步数据库连接成功。")
    # except Exception as e:
    #     print(f"数据库连接失败: {e}")

    # 可以在这里进行其他初始化操作，例如连接到消息队列、加载缓存等

    yield # 应用在此处运行

    # --- 应用关闭时执行 ---
    print(f"关闭应用: {settings.PROJECT_NAME}")
    # 示例: 关闭数据库引擎的连接池 (通常 SQLAlchemy 会自动处理，但显式关闭更安全)
    # if async_engine:
    #     await async_engine.dispose()
    #     print("异步数据库引擎已关闭。")
    # if sync_engine:
    #     sync_engine.dispose()
    #     print("同步数据库引擎已关闭。")


# --- FastAPI 应用实例 ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs", # Swagger UI
    redoc_url="/redoc", # ReDoc
    description=f"API for {settings.PROJECT_NAME}. Environment: {settings.APP_ENV}.",
    lifespan=lifespan, # 使用新的 lifespan 上下文管理器
    # debug=settings.DEBUG_MODE # debug 模式会影响异常处理等，通常通过 uvicorn --reload 控制
)

# --- CORS (跨源资源共享) 中间件 ---
if settings.CORS_ALLOWED_ORIGINS:
    allow_origins_list = []
    if isinstance(settings.CORS_ALLOWED_ORIGINS, str):
        if settings.CORS_ALLOWED_ORIGINS == "*":
            allow_origins_list = ["*"]
        else:
            allow_origins_list = [
                origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(',') if origin.strip()
            ]
    elif isinstance(settings.CORS_ALLOWED_ORIGINS, list):
        allow_origins_list = settings.CORS_ALLOWED_ORIGINS

    if allow_origins_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins_list,
            allow_credentials=True, # 是否允许携带 cookies
            allow_methods=["*"],    # 允许所有标准的 HTTP 方法
            allow_headers=["*"],    # 允许所有请求头
        )
        print(f"CORS 已启用，允许的源: {allow_origins_list}")
    else:
        print("CORS 未配置允许的源，未启用 CORS 中间件。")


# --- 包含 API 路由 ---
app.include_router(api_router_v1, prefix=settings.API_V1_STR)


# --- 根路径 ---
@app.get("/", tags=["Root"])
async def read_root():
    """
    应用根路径，提供基本信息和文档链接。
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.APP_ENV,
        "message": f"欢迎访问 {settings.PROJECT_NAME} API!",
        "documentation": [
            {"type": "Swagger UI", "url": app.docs_url},
            {"type": "ReDoc", "url": app.redoc_url},
            {"type": "OpenAPI JSON", "url": app.openapi_url},
        ],
        "debug_echo_endpoint": f"{settings.API_V1_STR}/debug/echo"
    }

# 如果你需要在应用启动时执行一些一次性任务，例如创建初始超级用户，
# 可以将其放在 lifespan 的启动部分，或者创建一个管理命令。
# from app.initial_data import init_db # 假设你有这个模块
# @app.on_event("startup") # 旧的事件处理器方式
# async def on_startup():
# await init_db() # 如果 init_db 是异步的