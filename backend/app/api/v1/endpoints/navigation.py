# backend/app/api/v1/endpoints/navigation.py
from fastapi import APIRouter, Depends, HTTPException, status, Path, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict

from app.api import deps # 依赖项 (如 get_async_db, get_current_active_user)
from app.crud.crud_navigation import ( # 导航 CRUD 操作
    crud_navigation_group,
    crud_navigation_item,
)
from app.schemas.navigation import ( # 导航 Pydantic schemas
    NavigationGroupCreate,
    NavigationGroupUpdate,
    NavigationGroupPublic,
    NavigationGroupWithItemsPublic, # 用于获取分组及其项
    NavigationItemCreate,
    NavigationItemUpdate,
    NavigationItemPublic,
)
from app.models.user import User as UserModel # SQLAlchemy 用户模型 (用于类型提示)
from app.models.navigation import NavigationGroup as NavigationGroupModel # 用于类型提示
from app.models.navigation import NavigationItem as NavigationItemModel # 用于类型提示

router = APIRouter()

# --- Navigation Group Endpoints ---

@router.post(
    "/groups",
    response_model=NavigationGroupPublic,
    status_code=status.HTTP_201_CREATED,
    summary="创建新的导航分组"
)
async def create_navigation_group(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    group_in: NavigationGroupCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> NavigationGroupPublic:
    """
    为当前认证用户创建一个新的导航分组。
    请求体应包含 `name` (必需) 和可选的 `description`, `order_index`。
    """
    new_group = await crud_navigation_group.create_group_for_user(
        db=db, obj_in=group_in, user_id=current_user.id
    )
    return new_group


@router.get(
    "/groups",
    response_model=List[NavigationGroupPublic], # 返回不带 items 的分组列表
    summary="获取当前用户的所有导航分组"
)
async def read_user_navigation_groups(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=200, description="每页最大记录数"),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[NavigationGroupPublic]:
    """
    获取当前认证用户的所有导航分组，按 `order_index` 和创建时间排序。
    支持分页。
    """
    groups = await crud_navigation_group.get_groups_by_user_id(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return groups


@router.get(
    "/groups/{group_id}",
    response_model=NavigationGroupWithItemsPublic, # 返回带 items 的单个分组详情
    summary="获取指定导航分组及其包含的导航项"
)
async def read_navigation_group_with_items(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    group_id: int = Path(..., description="要获取的导航分组ID", ge=1),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> NavigationGroupWithItemsPublic:
    """
    获取当前认证用户拥有的特定导航分组的详细信息，包括其下的所有导航项。
    """
    group = await crud_navigation_group.get_group_by_id(
        db=db, group_id=group_id, user_id=current_user.id
    )
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的导航分组或您没有权限访问。",
        )
    # group.items 应该已经被 SQLAlchemy 根据模型中的 lazy='selectin' 和 order_by 加载好了
    return group


@router.put(
    "/groups/{group_id}",
    response_model=NavigationGroupPublic,
    summary="更新指定的导航分组"
)
async def update_navigation_group(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    group_id: int = Path(..., description="要更新的导航分组ID", ge=1),
    group_in: NavigationGroupUpdate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> NavigationGroupPublic:
    """
    更新当前认证用户拥有的特定导航分组的信息。
    可更新 `name`, `description`, `order_index`。
    """
    db_group = await crud_navigation_group.get_group_by_id(
        db=db, group_id=group_id, user_id=current_user.id
    )
    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到要更新的导航分组或您没有权限访问。",
        )
    updated_group = await crud_navigation_group.update_group(
        db=db, db_obj=db_group, obj_in=group_in
    )
    return updated_group


@router.delete(
    "/groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT, # 成功删除通常返回 204
    summary="删除指定的导航分组"
)
async def delete_navigation_group(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    group_id: int = Path(..., description="要删除的导航分组ID", ge=1),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> None:
    """
    删除当前认证用户拥有的特定导航分组。
    该分组下的所有导航项也会被级联删除。
    """
    deleted_group = await crud_navigation_group.remove_group(
        db=db, group_id=group_id, user_id=current_user.id
    )
    if not deleted_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到要删除的导航分组或您没有权限访问。",
        )
    return None # 对于 204 No Content，不需要返回体


# --- Navigation Item Endpoints ---

@router.post(
    "/groups/{group_id}/items",
    response_model=NavigationItemPublic,
    status_code=status.HTTP_201_CREATED,
    summary="在指定导航分组下创建新的导航项"
)
async def create_navigation_item_for_group(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    group_id: int = Path(..., description="导航项所属的分组ID", ge=1),
    item_in: NavigationItemCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> NavigationItemPublic:
    """
    在当前认证用户拥有的特定导航分组下创建一个新的导航项。
    请求体应包含 `title`, `url` 和可选的 `icon_url`, `description`, `order_index`。
    """
    # CRUD 操作 create_item_in_group 内部会验证 group_id 是否属于 current_user
    new_item = await crud_navigation_item.create_item_in_group(
        db=db, obj_in=item_in, group_id=group_id, user_id=current_user.id
    )
    if not new_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # 或者 403 Forbidden
            detail="找不到指定的导航分组或您没有权限在此分组下创建导航项。",
        )
    return new_item


@router.get(
    "/groups/{group_id}/items",
    response_model=List[NavigationItemPublic],
    summary="获取指定导航分组下的所有导航项"
)
async def read_navigation_items_in_group(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    group_id: int = Path(..., description="导航项所属的分组ID", ge=1),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(200, ge=1, le=500, description="每页最大记录数"),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[NavigationItemPublic]:
    """
    获取当前认证用户拥有的特定导航分组下的所有导航项，按 `order_index` 和创建时间排序。
    支持分页。
    """
    # CRUD 操作 get_items_by_group_id 内部会验证 group_id 是否属于 current_user
    items = await crud_navigation_item.get_items_by_group_id(
        db=db, group_id=group_id, user_id=current_user.id, skip=skip, limit=limit
    )
    # 如果 CRUD 返回空列表表示分组不存在或不属于用户，这里不需要额外检查，直接返回空列表即可
    return items


@router.put(
    "/items/{item_id}", # 更新导航项通常直接通过 item_id，不需要 group_id 在路径中
    response_model=NavigationItemPublic,
    summary="更新指定的导航项"
)
async def update_navigation_item(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    item_id: int = Path(..., description="要更新的导航项ID", ge=1),
    item_in: NavigationItemUpdate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> NavigationItemPublic:
    """
    更新当前认证用户拥有的特定导航项的信息。
    可更新 `title`, `url`, `icon_url`, `description`, `order_index`。
    """
    db_item = await crud_navigation_item.get_item_by_id(
        db=db, item_id=item_id, user_id=current_user.id # 验证所有权
    )
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到要更新的导航项或您没有权限访问。",
        )
    updated_item = await crud_navigation_item.update_item(
        db=db, db_obj=db_item, obj_in=item_in
    )
    return updated_item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除指定的导航项"
)
async def delete_navigation_item(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    item_id: int = Path(..., description="要删除的导航项ID", ge=1),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> None:
    """
    删除当前认证用户拥有的特定导航项。
    """
    deleted_item = await crud_navigation_item.remove_item(
        db=db, item_id=item_id, user_id=current_user.id # 验证所有权
    )
    if not deleted_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到要删除的导航项或您没有权限访问。",
        )
    return None


@router.post(
    "/groups/{group_id}/items/reorder",
    status_code=status.HTTP_200_OK, # 或者 204 No Content 如果不返回特定内容
    response_model=Dict[str, str], # 简单的成功消息
    summary="重新排序指定导航分组下的导航项"
)
async def reorder_navigation_items(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    group_id: int = Path(..., description="要重新排序导航项的分组ID", ge=1),
    # 请求体期望一个包含 item_ids 列表的 JSON 对象，例如: {"ordered_item_ids": [3, 1, 2]}
    payload: Dict[str, List[int]] = Body(..., example={"ordered_item_ids": [1, 2, 3]}),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> Dict[str, str]:
    """
    根据提供的 ID 列表重新排序指定导航分组下的导航项。
    请求体应为 `{"ordered_item_ids": [id1, id2, id3, ...]}`，其中 ID 按新顺序排列。
    """
    ordered_item_ids = payload.get("ordered_item_ids")
    if ordered_item_ids is None or not isinstance(ordered_item_ids, list):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="请求体必须包含 'ordered_item_ids' 列表。"
        )

    success = await crud_navigation_item.reorder_items_in_group(
        db=db, group_id=group_id, user_id=current_user.id, ordered_item_ids=ordered_item_ids
    )
    if not success:
        # CRUD 中的 reorder_items_in_group 如果返回 False，可能表示分组不存在或ID无效
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # 或者 404
            detail="重新排序失败。请检查分组ID和导航项ID是否有效且属于该分组。"
        )
    return {"message": "导航项已成功重新排序。"}