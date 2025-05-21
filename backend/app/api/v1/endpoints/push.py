# backend/app/api/v1/endpoints/push.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Body, Request, Header
from app.crud.crud_user import user as crud_user
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional, Union

from app.api import deps # 依赖项
from app.crud.crud_push import ( # 推送 CRUD 操作
    crud_push_source,
    crud_push_subscription,
    crud_push_message,
)
from app.schemas.push import ( # 推送 Pydantic schemas
    PushSourceCreate,
    PushSourceUpdate,
    PushSourcePublic,
    PushSubscriptionCreate,
    PushSubscriptionUpdate,
    PushSubscriptionPublic,
    WebhookMessagePayload, # 用于接收外部消息
    PushMessageUpdate, # 用户更新消息状态
    PushMessagePublic,
)
from app.models.user import User as UserModel
from app.models.push import PushSource as PushSourceModel # 用于类型提示
from app.core.config import settings # 如果需要配置项，例如 Webhook 密钥

# 配置日志记录器
logger = logging.getLogger(__name__)

router = APIRouter()

# --- PushSource Endpoints (Admin Operations) ---

@router.post(
    "/sources",
    response_model=PushSourcePublic,
    status_code=status.HTTP_201_CREATED,
    summary=" (管理员) 创建新的推送来源"
)
async def create_push_source(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    source_in: PushSourceCreate,
    current_admin: UserModel = Depends(deps.get_current_active_superuser) # 需要超级用户权限
) -> PushSourcePublic:
    """
    创建一个新的推送来源。例如，配置一个钉钉机器人或一个通用的 Webhook 接收点。
    仅限超级管理员操作。
    """
    existing_source = await crud_push_source.get_source_by_name(db, name=source_in.name)
    if existing_source:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"名为 '{source_in.name}' 的推送来源已存在。",
        )

    # 根据source_type对config进行校验
    if source_in.source_type == "webhook" and (not source_in.config or "url" not in source_in.config):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Webhook类型的推送来源必须在config中提供url字段"
        )

    # 创建推送来源
    db_source = await crud_push_source.create_source(db=db, obj_in=source_in)

    # 将SQLAlchemy模型转换为Pydantic模型
    # 使用from_orm方法，它会自动处理SQLAlchemy列到Pydantic字段的转换
    return PushSourcePublic.model_validate(db_source)


@router.get(
    "/sources",
    response_model=List[PushSourcePublic],
    summary=" (管理员或认证用户) 获取推送来源列表"
)
async def read_push_sources(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    only_active: bool = Query(True, description="仅返回激活的推送来源 (对普通用户默认为True)"),
    # current_user: UserModel = Depends(deps.get_current_active_user) # 普通用户也可以查看来源列表，以便订阅
    # 如果只有管理员能看所有，普通用户只能看 active，则需要调整依赖和逻辑
    # 这里简化为：默认只看 active，管理员可以通过参数调整
    current_user: Optional[UserModel] = Depends(deps.get_current_user) # 允许匿名或认证用户访问
) -> List[PushSourcePublic]:
    """
    获取推送来源列表。
    - 普通认证用户或匿名用户通常只能看到激活的来源。
    - 管理员可以通过 `only_active=False` 查看所有来源。
    """
    is_admin = current_user and crud_user.is_superuser(current_user) # crud_user 需要导入
    if not is_admin and not only_active: # 非管理员尝试查看非激活来源
        effective_only_active = True
    else:
        effective_only_active = only_active

    db_sources = await crud_push_source.get_multi_sources(db=db, skip=skip, limit=limit, only_active=effective_only_active)

    # 将SQLAlchemy模型列表转换为Pydantic模型列表
    return [PushSourcePublic.model_validate(source) for source in db_sources]


@router.get(
    "/sources/{source_id}",
    response_model=PushSourcePublic,
    summary=" (管理员) 获取指定推送来源详情"
)
async def read_push_source_details(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    source_id: int = Path(..., ge=1),
    current_admin: UserModel = Depends(deps.get_current_active_superuser)
) -> PushSourcePublic:
    """
    获取特定推送来源的详细信息。
    仅限超级管理员操作（因为可能包含敏感配置的引用）。
    """
    db_source = await crud_push_source.get_source_by_id(db, source_id=source_id)
    if not db_source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到指定的推送来源。")

    # 将SQLAlchemy模型转换为Pydantic模型
    return PushSourcePublic.model_validate(db_source)


@router.put(
    "/sources/{source_id}",
    response_model=PushSourcePublic,
    summary=" (管理员) 更新指定推送来源"
)
async def update_push_source(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    source_id: int = Path(..., ge=1),
    source_in: PushSourceUpdate,
    current_admin: UserModel = Depends(deps.get_current_active_superuser)
) -> PushSourcePublic:
    """
    更新特定推送来源的信息。
    仅限超级管理员操作。
    """
    db_source = await crud_push_source.get_source_by_id(db, source_id=source_id)
    if not db_source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到要更新的推送来源。")

    if source_in.name and source_in.name != db_source.name:
        existing_source_by_name = await crud_push_source.get_source_by_name(db, name=source_in.name)
        if existing_source_by_name and existing_source_by_name.id != source_id:
            raise HTTPException(status_code=409, detail=f"名为 '{source_in.name}' 的推送来源已存在。")

    updated_source = await crud_push_source.update_source(db=db, db_obj=db_source, obj_in=source_in)
    return PushSourcePublic.model_validate(updated_source)


@router.delete(
    "/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=" (管理员) 删除指定推送来源"
)
async def delete_push_source(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    source_id: int = Path(..., ge=1),
    current_admin: UserModel = Depends(deps.get_current_active_superuser)
) -> None:
    """
    删除特定的推送来源。
    相关的订阅和（可能）消息也会被级联删除（取决于模型定义）。
    仅限超级管理员操作。
    """
    deleted_source = await crud_push_source.remove_source(db, source_id=source_id)
    if not deleted_source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到要删除的推送来源。")
    return None


# --- PushSubscription Endpoints (User Operations) ---

@router.post(
    "/subscriptions",
    response_model=PushSubscriptionPublic,
    status_code=status.HTTP_201_CREATED,
    summary="用户订阅推送来源"
)
async def create_user_subscription(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    subscription_in: PushSubscriptionCreate, # 包含 source_id 和可选的 user_specific_config, is_active
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> PushSubscriptionPublic:
    """
    当前认证用户订阅一个推送来源。
    如果用户已订阅该来源，则可能返回错误或更新现有订阅状态。
    """
    # 1. 检查来源是否存在且激活
    source_to_subscribe = await crud_push_source.get_source_by_id(db, source_id=subscription_in.source_id)
    if not source_to_subscribe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的推送来源。"
        )

    is_active = getattr(source_to_subscribe, 'is_active', None)
    if is_active is not None and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该推送来源未激活，无法订阅。"
        )

    # 2. 检查是否已订阅
    existing_subscription = await crud_push_subscription.get_subscription_by_user_and_source(
        db, user_id=current_user.id, source_id=subscription_in.source_id
    )
    if existing_subscription:
        # 如果已存在，可以选择更新它（例如，如果它之前是 inactive）或直接返回冲突
        existing_is_active = getattr(existing_subscription, 'is_active', False)
        if not existing_is_active and subscription_in.is_active:
            # 如果之前是禁用，现在要启用
            updated_sub = await crud_push_subscription.update_subscription(
                db,
                db_obj=existing_subscription,
                obj_in={"is_active": True, "user_specific_config": subscription_in.user_specific_config}
            )
            return PushSubscriptionPublic.model_validate(updated_sub)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="您已订阅此推送来源。"
        )

    # 3. 创建订阅
    new_subscription = await crud_push_subscription.create_subscription(
        db=db, obj_in=subscription_in, user_id=current_user.id
    )

    # 创建Pydantic模型并返回
    result = PushSubscriptionPublic.model_validate(new_subscription)
    # 如果需要，可以手动设置source字段
    result.source = PushSourcePublic.model_validate(source_to_subscribe) if source_to_subscribe else None
    return result


@router.get(
    "/subscriptions",
    response_model=List[PushSubscriptionPublic],
    summary="获取当前用户的推送订阅列表"
)
async def read_user_subscriptions(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    only_active: bool = Query(False, description="仅返回激活的订阅"), # 用户可能想看所有订阅，包括禁用的
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[PushSubscriptionPublic]:
    """
    获取当前认证用户的所有推送订阅列表。
    """
    db_subscriptions = await crud_push_subscription.get_subscriptions_by_user_id(
        db=db, user_id=current_user.id, skip=skip, limit=limit, only_active=only_active
    )

    # 创建结果列表
    result = []

    # 为每个订阅创建Pydantic模型
    for sub in db_subscriptions:
        # 创建基本的订阅模型
        subscription = PushSubscriptionPublic.model_validate(sub)

        # 如果需要，加载并设置source字段
        if hasattr(sub, 'source_id') and getattr(sub, 'source_id', None):
            source_id = int(getattr(sub, 'source_id'))
            db_source = await crud_push_source.get_source_by_id(db, source_id=source_id)
            if db_source:
                subscription.source = PushSourcePublic.model_validate(db_source)

        result.append(subscription)

    return result


@router.put(
    "/subscriptions/{subscription_id}",
    response_model=PushSubscriptionPublic,
    summary="更新用户的推送订阅"
)
async def update_user_subscription(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    subscription_id: int = Path(..., ge=1),
    subscription_in: PushSubscriptionUpdate, # 只允许更新 is_active 和 user_specific_config
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> PushSubscriptionPublic:
    """
    更新当前认证用户的特定推送订阅（例如，启用/禁用，修改用户特定配置）。
    """
    db_subscription = await crud_push_subscription.get_subscription_by_id(
        db, subscription_id=subscription_id, user_id=current_user.id
    )
    if not db_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到指定的订阅。")

    updated_subscription = await crud_push_subscription.update_subscription(
        db, db_obj=db_subscription, obj_in=subscription_in
    )

    # 创建Pydantic模型
    result = PushSubscriptionPublic.model_validate(updated_subscription)

    # 如果需要，加载并设置source字段
    if hasattr(updated_subscription, 'source_id') and getattr(updated_subscription, 'source_id', None):
        source_id = int(getattr(updated_subscription, 'source_id'))
        db_source = await crud_push_source.get_source_by_id(db, source_id=source_id)
        if db_source:
            result.source = PushSourcePublic.model_validate(db_source)

    return result


@router.delete(
    "/subscriptions/{subscription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="用户取消订阅推送来源"
)
async def delete_user_subscription(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    subscription_id: int = Path(..., ge=1),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> None:
    """
    当前认证用户取消对特定推送来源的订阅。
    """
    deleted_subscription = await crud_push_subscription.remove_subscription(
        db, subscription_id=subscription_id, user_id=current_user.id
    )
    if not deleted_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到要取消的订阅。")
    return None


# --- PushMessage Endpoints (User Operations) ---

@router.get(
    "/messages",
    response_model=List[PushMessagePublic],
    summary="获取当前用户的推送消息列表"
)
async def read_user_push_messages(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    source_id: Optional[int] = Query(None, description="按来源ID筛选"),
    status: Optional[str] = Query(None, description="按消息状态筛选 (e.g., 'unread', 'read')"),
    unread_only: Optional[bool] = Query(None, description="仅返回未读消息"),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[PushMessagePublic]:
    """
    获取当前认证用户收到的推送消息列表，支持分页和筛选。
    """
    db_messages = await crud_push_message.get_messages_for_user(
        db, user_id=current_user.id, skip=skip, limit=limit,
        source_id=source_id, status=status, unread_only=unread_only
    )

    # 创建结果列表
    result = []

    # 为每个消息创建Pydantic模型
    for msg in db_messages:
        # 创建基本的消息模型
        message = PushMessagePublic.model_validate(msg)

        # 如果需要，加载并设置source字段
        if hasattr(msg, 'source_id') and getattr(msg, 'source_id', None):
            source_id = int(getattr(msg, 'source_id'))
            db_source = await crud_push_source.get_source_by_id(db, source_id=source_id)
            if db_source:
                message.source = PushSourcePublic.model_validate(db_source)

        result.append(message)

    return result


@router.put(
    "/messages/{message_id}/status",
    response_model=PushMessagePublic,
    summary="更新用户消息的状态 (例如，标记为已读)"
)
async def update_user_message_status(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    message_id: int = Path(..., ge=1),
    message_in: PushMessageUpdate, # 请求体包含 new_status, 例如 {"status": "read"}
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> PushMessagePublic:
    """
    更新当前认证用户拥有的特定消息的状态。
    主要用于将消息标记为“已读”或“已归档”。
    """
    if not message_in.status: # 确保请求体中提供了 status
        raise HTTPException(status_code=422, detail="请求体中必须包含 'status' 字段。")

    updated_db_message = await crud_push_message.update_message_status(
        db, message_id=message_id, user_id=current_user.id, new_status=message_in.status
    )
    if not updated_db_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到指定的消息或您没有权限修改。")

    # 创建Pydantic模型
    result = PushMessagePublic.model_validate(updated_db_message)

    # 如果需要，加载并设置source字段
    if hasattr(updated_db_message, 'source_id') and getattr(updated_db_message, 'source_id', None):
        source_id = int(getattr(updated_db_message, 'source_id'))
        db_source = await crud_push_source.get_source_by_id(db, source_id=source_id)
        if db_source:
            result.source = PushSourcePublic.model_validate(db_source)

    return result


@router.post(
    "/messages/mark-all-read",
    response_model=Dict[str, Any],
    summary="将用户的所有（或特定来源的）未读消息标记为已读"
)
async def mark_all_user_messages_as_read(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    source_id: Optional[int] = Query(None, description="可选：仅标记特定来源的未读消息"),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """
    将当前认证用户的所有未读消息（或特定来源的未读消息）标记为“已读”。
    返回受影响的消息数量。
    """
    updated_count = await crud_push_message.mark_all_messages_as_read_for_user(
        db, user_id=current_user.id, source_id=source_id
    )
    return {"message": f"{updated_count} 条消息已标记为已读。", "updated_count": updated_count}


# --- Webhook Endpoint for Receiving External Messages ---
# 这个端点通常是公开的，或者使用特定的 token/密钥进行验证，而不是标准的 OAuth2 用户认证

@router.post(
    "/webhooks/ingress/{source_identifier}", # source_identifier 可以是 PushSource 的 id 或一个唯一的字符串标识符
    status_code=status.HTTP_202_ACCEPTED, # 202 Accepted 表示请求已接收，正在处理
    summary=" (Webhook) 接收外部系统推送来的消息",
    tags=["Webhooks"] # 单独分组以便于API文档组织
)
async def receive_webhook_message(
    *,
    db: AsyncSession = Depends(deps.get_async_db), # Webhook 也需要数据库会话
    source_identifier: str = Path(..., description="推送来源的唯一标识符"),
    payload: WebhookMessagePayload, # 使用专门的 schema 接收 Webhook 数据
    request: Request, # 用来获取请求头等信息，例如验证签名
    webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret") # 从请求头获取密钥
) -> Dict[str, Union[str, int]]:
    """
    用于接收来自已配置的外部推送来源（例如自定义 Webhook、第三方服务回调）的消息。
    系统会根据 `source_identifier` 找到对应的 `PushSource`，
    然后将消息分发给所有订阅了该来源的活跃用户。

    **安全要求**:
    - 必须提供有效的 X-Webhook-Secret 头，与推送来源配置中的secret匹配
    - 请求IP必须在允许列表中（如果来源配置了IP白名单）
    - 某些来源可能需要验证签名（取决于source_type）
    """
    # 1. 根据 source_identifier 查找 PushSource
    db_source: Optional[PushSourceModel] = None
    try:
        source_id_int = int(source_identifier)
        db_source = await crud_push_source.get_source_by_id(db, source_id=source_id_int)
    except ValueError: # 如果 source_identifier 不是数字，则尝试按其他唯一标识符查找
        # 实现标识符查找逻辑
        # 这里可以添加 get_source_by_identifier 方法的实现
        pass

    if not db_source:
        logger.warning(f"未找到推送来源标识符: {source_identifier}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到推送来源标识符: {source_identifier}"
        )

    is_active = getattr(db_source, 'is_active', None)
    if is_active is not None and not is_active:
        logger.warning(f"推送来源未激活: {source_identifier}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"推送来源 '{source_identifier}' 未激活"
        )

    # 2. 验证 Webhook 请求的合法性
    # 2.1 验证密钥
    config = getattr(db_source, 'config', None)
    if config and isinstance(config, dict) and "secret" in config:
        config_secret = config.get("secret")
        if not webhook_secret or webhook_secret != config_secret:
            logger.warning(f"Webhook密钥验证失败: 提供的密钥与配置不匹配")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Webhook 密钥无效"
            )

    # 2.2 检查IP白名单（如果配置了）
    config = getattr(db_source, 'config', None)
    if (config and
        isinstance(config, dict) and
        "ip_whitelist" in config):
        # 获取客户端IP地址
        client_ip = ""
        x_forwarded_for = request.headers.get("x-forwarded-for", "")
        if x_forwarded_for:
            client_ip = str(x_forwarded_for)
        else:
            # 尝试不同的方式获取客户端IP
            try:
                client_ip = str(request.client)
            except:
                client_ip = "unknown"

        ip_whitelist = config.get("ip_whitelist", [])
        if ip_whitelist and client_ip not in ip_whitelist:
            logger.warning(f"IP白名单验证失败: {client_ip} 不在允许列表 {ip_whitelist} 中")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"IP地址 {client_ip} 不在允许列表中"
            )

    # 2.3 验证签名（根据来源类型）
    source_type = getattr(db_source, 'source_type', None)
    config = getattr(db_source, 'config', None)

    if (source_type == "github" and
        config and
        isinstance(config, dict) and
        "webhook_secret" in config):

        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            logger.warning(f"GitHub webhook验证失败: 缺少签名头")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="缺少 GitHub 签名头"
            )

        # 实现GitHub签名验证
        import hmac
        import hashlib

        raw_body = await request.body()
        webhook_secret = config.get("webhook_secret", "")
        if not webhook_secret:
            logger.error("GitHub webhook配置错误: webhook_secret为空")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook配置错误: webhook_secret为空"
            )

        secret = webhook_secret.encode('utf-8')
        expected_signature = "sha256=" + hmac.new(
            secret,
            raw_body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.warning(f"GitHub签名验证失败: {signature} != {expected_signature}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="GitHub 签名验证失败"
            )


    # 3. 将接收到的消息分发给订阅者
    try:
        created_messages = await crud_push_message.create_messages_for_subscribers(
            db=db,
            source_id=db_source.id,
            title=payload.title,
            content=payload.content,
            content_type=payload.content_type or "text/plain", # 使用默认值
            raw_data=payload.model_dump() # 将整个接收到的 payload 作为 raw_data 存储
        )

        # 记录webhook接收日志
        logger.info(
            f"Webhook接收成功: source_id={db_source.id}, "
            f"source_name='{db_source.name}', messages_created={len(created_messages)}"
        )

        # 4. 触发实际的推送通知（使用后台任务）
        # 这里我们可以使用异步任务队列，但为简单起见，先记录日志
        logger.info(f"需要发送 {len(created_messages)} 条实际通知")

        # 实际项目中，这里应该调用后台任务队列
        # from app.worker import send_notifications_task
        # task_id = await send_notifications_task.delay([msg.id for msg in created_messages])
        # logger.info(f"已提交通知发送任务: task_id={task_id}")

        return {
            "message": "消息已接收并开始处理。",
            "received_messages_for_users": len(created_messages),
            "status": "success"
        }
    except Exception as e:
        # 记录错误并返回适当的错误响应
        logger.error(f"处理webhook消息时出错: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理消息时发生错误: {str(e)}"
        )

# 确保导入 crud_user (如果 /sources 接口的权限判断需要)
from app.crud.crud_user import user as crud_user