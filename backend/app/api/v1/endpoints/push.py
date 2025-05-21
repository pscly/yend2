# backend/app/api/v1/endpoints/push.py
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Body, Request
from app.crud.crud_user import user as crud_user 
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

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
    # 可以在这里根据 source_in.source_type 对 source_in.config 进行更详细的校验
    # 例如，如果 type 是 'webhook'，config 中必须有 'url'
    new_source = await crud_push_source.create_source(db=db, obj_in=source_in)
    return new_source


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

    sources = await crud_push_source.get_multi_sources(db=db, skip=skip, limit=limit, only_active=effective_only_active)
    return sources


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
    source = await crud_push_source.get_source_by_id(db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到指定的推送来源。")
    # 注意：PushSourcePublic schema 应该处理 config 字段的敏感信息过滤
    return source


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
    return updated_source


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
    if not source_to_subscribe or not source_to_subscribe.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的推送来源或该来源未激活。"
        )

    # 2. 检查是否已订阅
    existing_subscription = await crud_push_subscription.get_subscription_by_user_and_source(
        db, user_id=current_user.id, source_id=subscription_in.source_id
    )
    if existing_subscription:
        # 如果已存在，可以选择更新它（例如，如果它之前是 inactive）或直接返回冲突
        if not existing_subscription.is_active and subscription_in.is_active: # 如果之前是禁用，现在要启用
            return await crud_push_subscription.update_subscription(
                db, db_obj=existing_subscription, obj_in={"is_active": True, "user_specific_config": subscription_in.user_specific_config}
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="您已订阅此推送来源。"
        )

    # 3. 创建订阅
    new_subscription = await crud_push_subscription.create_subscription(
        db=db, obj_in=subscription_in, user_id=current_user.id
    )
    # 可以在返回的 PushSubscriptionPublic 中填充 source 信息
    new_subscription.source = source_to_subscribe # 手动填充关系以便 schema 序列化
    return new_subscription


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
    subscriptions = await crud_push_subscription.get_subscriptions_by_user_id(
        db=db, user_id=current_user.id, skip=skip, limit=limit, only_active=only_active
    )
    # 为了在响应中包含 source 信息，需要手动加载或确保 lazy='selectin'/'joined' 在模型关系中有效
    # 或者在 CRUD 中返回时就处理好
    for sub in subscriptions: # 确保 source 被加载以便 Pydantic 序列化
        if sub.source_id and not sub.source: # 简单的检查，实际可能需要更健壮的加载
            sub.source = await crud_push_source.get_source_by_id(db, source_id=sub.source_id)
    return subscriptions


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
    if updated_subscription.source_id and not updated_subscription.source:
        updated_subscription.source = await crud_push_source.get_source_by_id(db, source_id=updated_subscription.source_id)
    return updated_subscription


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
    messages = await crud_push_message.get_messages_for_user(
        db, user_id=current_user.id, skip=skip, limit=limit,
        source_id=source_id, status=status, unread_only=unread_only
    )
    # 同样，为了在响应中包含 source 信息，需要确保加载
    for msg in messages:
        if msg.source_id and not msg.source:
            msg.source = await crud_push_source.get_source_by_id(db, source_id=msg.source_id)
    return messages


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

    updated_message = await crud_push_message.update_message_status(
        db, message_id=message_id, user_id=current_user.id, new_status=message_in.status
    )
    if not updated_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到指定的消息或您没有权限修改。")
    if updated_message.source_id and not updated_message.source:
        updated_message.source = await crud_push_source.get_source_by_id(db, source_id=updated_message.source_id)
    return updated_message


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
    # dependencies=[Depends(verify_webhook_token)] # 可选：添加一个验证 Webhook 请求的依赖项
    # tags=["Webhooks"] # 可以单独分组
)
async def receive_webhook_message(
    *,
    db: AsyncSession = Depends(deps.get_async_db), # Webhook 也需要数据库会话
    source_identifier: str = Path(..., description="推送来源的唯一标识符"),
    payload: WebhookMessagePayload, # 使用专门的 schema 接收 Webhook 数据
    request: Request # 可以用来获取请求头等信息，例如验证签名
    # webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret") # 示例：从请求头获取密钥
) -> Dict[str, str]:
    """
    用于接收来自已配置的外部推送来源（例如自定义 Webhook、第三方服务回调）的消息。
    系统会根据 `source_identifier` 找到对应的 `PushSource`，
    然后将消息分发给所有订阅了该来源的活跃用户。

    **安全注意**: 此端点应受到保护，例如通过检查预共享密钥、验证签名或 IP 白名单。
    """
    # 1. 验证 Webhook 请求的合法性 (重要!)
    #    - 检查 IP 白名单 (如果配置)
    #    - 验证签名 (例如 HMAC SHA256，如果第三方服务提供)
    #    - 检查预共享密钥 (例如在 PushSource.config 中存储一个 secret，并在请求头或参数中传递)
    #    这里简化，不包含完整的安全验证逻辑

    # 2. 根据 source_identifier 查找 PushSource
    #    假设 source_identifier 可以是 PushSource 的 ID (转为int) 或一个唯一的字符串字段 (如 PushSource.identifier)
    db_source: Optional[PushSourceModel] = None
    try:
        source_id_int = int(source_identifier)
        db_source = await crud_push_source.get_source_by_id(db, source_id=source_id_int)
    except ValueError: # 如果 source_identifier 不是数字，则尝试按其他唯一标识符查找
        # db_source = await crud_push_source.get_source_by_identifier(db, identifier=source_identifier) # 假设有这个方法
        pass # 如果没有其他标识符，则保持 db_source 为 None

    if not db_source or not db_source.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到或未激活的推送来源标识符: {source_identifier}"
        )

    # (可选) 进一步验证 payload 是否符合 db_source.config 中的预期，或 webhook_secret 是否匹配
    # if db_source.config and db_source.config.get("secret") and webhook_secret != db_source.config.get("secret"):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Webhook 密钥无效")


    # 3. 将接收到的消息分发给订阅者
    #    crud_push_message.create_messages_for_subscribers 会处理查找订阅者并创建消息记录的逻辑
    created_messages = await crud_push_message.create_messages_for_subscribers(
        db=db,
        source_id=db_source.id,
        title=payload.title,
        content=payload.content,
        content_type=payload.content_type or "text/plain", # 使用默认值
        raw_data=payload.model_dump() # 将整个接收到的 payload 作为 raw_data 存储
    )

    # 4. (可选) 触发实际的推送通知 (例如发送邮件、调用 App 推送 API 等)
    #    这部分逻辑通常是异步的，并且可能比较耗时，可以考虑放入后台任务队列 (如 Celery, ARQ)
    #    for msg in created_messages:
    #        await send_actual_notification_to_user(user_id=msg.user_id, title=msg.title, content=msg.content)

    return {"message": "消息已接收并开始处理。", "received_messages_for_users": len(created_messages)}

# 确保导入 crud_user (如果 /sources 接口的权限判断需要)
from app.crud.crud_user import user as crud_user