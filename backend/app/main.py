# backend/app/main.py
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager # 用于 FastAPI 的 lifespan (替代 on_event)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router_v1
from app.core.config import settings
from app.api import deps
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

# --- 匿名推送接口 ---
@app.api_route("/d1", methods=["GET", "POST"], tags=["Anonymous Push"])
async def anonymous_push(request: Request, db: AsyncSession = Depends(deps.get_async_db)):
    """
    匿名推送消息接口，支持GET和POST请求。

    - GET请求：通过URL参数接收 bt(标题) 和 content(内容)
    - POST请求：支持表单数据和JSON格式，接收 bt(标题) 和 content(内容)

    响应始终包含：
    - 当前时间（格式化为易读的日期时间字符串）
    - 当前请求的完整URL
    - 请求中的所有参数（作为字典）

    示例：
    - GET: /d1?bt=标题&content=内容
    - POST (表单): /d1 (表单数据: bt=标题&content=内容)
    - POST (JSON): /d1 (JSON数据: {"bt": "标题", "content": "内容"})
    """
    from app.crud.crud_push import crud_push_source, crud_push_message
    import logging
    import datetime

    logger = logging.getLogger(__name__)

    # 获取请求数据（合并所有可能的来源）
    data = {}

    # 1. 处理URL参数（适用于GET和POST）
    for key, value in request.query_params.items():
        data[key] = value

    # 2. 处理POST请求的表单或JSON数据
    if request.method == "POST":
        content_type = request.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            # 处理JSON数据
            try:
                json_data = await request.json()
                data.update(json_data)
            except Exception as e:
                logger.error(f"解析JSON数据失败: {str(e)}")
                return {
                    "error": f"无法解析JSON数据: {str(e)}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": str(request.url),
                    "params": dict(request.query_params)
                }

        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            # 处理表单数据
            try:
                form_data = await request.form()
                for key, value in form_data.items():
                    data[key] = value
            except Exception as e:
                logger.error(f"解析表单数据失败: {str(e)}")
                return {
                    "error": f"无法解析表单数据: {str(e)}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": str(request.url),
                    "params": dict(request.query_params)
                }

    # 准备基本响应信息
    response_data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": str(request.url),
        "params": data
    }

    # 检查是否有参数
    if not data:
        response_data["message"] = "没有参数"
        return response_data

    # 获取标题和内容参数
    title = data.get("bt")
    content = data.get("content")

    # 如果没有bt或content参数，直接返回基本信息
    if not title and not content:
        response_data["message"] = "未提供bt或content参数"
        return response_data

    # 如果只有标题没有内容，或者只有内容没有标题，也返回基本信息
    if not title or not content:
        response_data["message"] = "提供了部分参数"
        response_data["has_title"] = bool(title)
        response_data["has_content"] = bool(content)
        return response_data

    # 查找默认的推送来源（或创建一个）
    source_name = "匿名推送"
    db_source = await crud_push_source.get_source_by_name(db, name=source_name)

    if not db_source:
        # 如果不存在默认的匿名推送来源，则创建一个
        from app.schemas.push import PushSourceCreate
        source_data = PushSourceCreate(
            name=source_name,
            source_type="anonymous",
            description="用于匿名推送消息的默认来源",
            is_active=True,
            config={"anonymous": True}
        )
        db_source = await crud_push_source.create_source(db, obj_in=source_data)
        logger.info(f"已创建默认的匿名推送来源: {source_name}")

    # 推送消息给所有订阅者
    try:
        created_messages = await crud_push_message.create_messages_for_subscribers(
            db=db,
            source_id=db_source.id,
            title=title,
            content=content,
            content_type="text/plain",
            raw_data=data
        )

        # 添加推送结果到响应
        response_data.update({
            "success": True,
            "message": "消息已成功推送",
            "recipients_count": len(created_messages),
            "title": title,
            "content": content
        })

        return response_data
    except Exception as e:
        logger.error(f"推送消息失败: {str(e)}")
        response_data.update({
            "error": f"推送消息失败: {str(e)}",
            "title": title,
            "content": content
        })
        return response_data

# 如果你需要在应用启动时执行一些一次性任务，例如创建初始超级用户，
# 可以将其放在 lifespan 的启动部分，或者创建一个管理命令。
# from app.initial_data import init_db # 假设你有这个模块
# @app.on_event("startup") # 旧的事件处理器方式
# async def on_startup():
# await init_db() # 如果 init_db 是异步的