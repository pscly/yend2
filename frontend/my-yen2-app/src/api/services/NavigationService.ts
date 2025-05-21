/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NavigationGroupCreate } from '../models/NavigationGroupCreate';
import type { NavigationGroupPublic } from '../models/NavigationGroupPublic';
import type { NavigationGroupUpdate } from '../models/NavigationGroupUpdate';
import type { NavigationGroupWithItemsPublic } from '../models/NavigationGroupWithItemsPublic';
import type { NavigationItemCreate } from '../models/NavigationItemCreate';
import type { NavigationItemPublic } from '../models/NavigationItemPublic';
import type { NavigationItemUpdate } from '../models/NavigationItemUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class NavigationService {
    /**
     * 创建新的导航分组
     * 为当前认证用户创建一个新的导航分组。
     * 请求体应包含 `name` (必需) 和可选的 `description`, `order_index`。
     * @param requestBody
     * @returns NavigationGroupPublic Successful Response
     * @throws ApiError
     */
    public static createNavigationGroupApiV1NavigationGroupsPost(
        requestBody: NavigationGroupCreate,
    ): CancelablePromise<NavigationGroupPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/navigation/groups',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取当前用户的所有导航分组
     * 获取当前认证用户的所有导航分组，按 `order_index` 和创建时间排序。
     * 支持分页。
     * @param skip 跳过的记录数
     * @param limit 每页最大记录数
     * @returns NavigationGroupPublic Successful Response
     * @throws ApiError
     */
    public static readUserNavigationGroupsApiV1NavigationGroupsGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<NavigationGroupPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/navigation/groups',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取指定导航分组及其包含的导航项
     * 获取当前认证用户拥有的特定导航分组的详细信息，包括其下的所有导航项。
     * @param groupId 要获取的导航分组ID
     * @returns NavigationGroupWithItemsPublic Successful Response
     * @throws ApiError
     */
    public static readNavigationGroupWithItemsApiV1NavigationGroupsGroupIdGet(
        groupId: number,
    ): CancelablePromise<NavigationGroupWithItemsPublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/navigation/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 更新指定的导航分组
     * 更新当前认证用户拥有的特定导航分组的信息。
     * 可更新 `name`, `description`, `order_index`。
     * @param groupId 要更新的导航分组ID
     * @param requestBody
     * @returns NavigationGroupPublic Successful Response
     * @throws ApiError
     */
    public static updateNavigationGroupApiV1NavigationGroupsGroupIdPut(
        groupId: number,
        requestBody: NavigationGroupUpdate,
    ): CancelablePromise<NavigationGroupPublic> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/navigation/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 删除指定的导航分组
     * 删除当前认证用户拥有的特定导航分组。
     * 该分组下的所有导航项也会被级联删除。
     * @param groupId 要删除的导航分组ID
     * @returns void
     * @throws ApiError
     */
    public static deleteNavigationGroupApiV1NavigationGroupsGroupIdDelete(
        groupId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/navigation/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 在指定导航分组下创建新的导航项
     * 在当前认证用户拥有的特定导航分组下创建一个新的导航项。
     * 请求体应包含 `title`, `url` 和可选的 `icon_url`, `description`, `order_index`。
     * @param groupId 导航项所属的分组ID
     * @param requestBody
     * @returns NavigationItemPublic Successful Response
     * @throws ApiError
     */
    public static createNavigationItemForGroupApiV1NavigationGroupsGroupIdItemsPost(
        groupId: number,
        requestBody: NavigationItemCreate,
    ): CancelablePromise<NavigationItemPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/navigation/groups/{group_id}/items',
            path: {
                'group_id': groupId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取指定导航分组下的所有导航项
     * 获取当前认证用户拥有的特定导航分组下的所有导航项，按 `order_index` 和创建时间排序。
     * 支持分页。
     * @param groupId 导航项所属的分组ID
     * @param skip 跳过的记录数
     * @param limit 每页最大记录数
     * @returns NavigationItemPublic Successful Response
     * @throws ApiError
     */
    public static readNavigationItemsInGroupApiV1NavigationGroupsGroupIdItemsGet(
        groupId: number,
        skip?: number,
        limit: number = 200,
    ): CancelablePromise<Array<NavigationItemPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/navigation/groups/{group_id}/items',
            path: {
                'group_id': groupId,
            },
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 更新指定的导航项
     * 更新当前认证用户拥有的特定导航项的信息。
     * 可更新 `title`, `url`, `icon_url`, `description`, `order_index`。
     * @param itemId 要更新的导航项ID
     * @param requestBody
     * @returns NavigationItemPublic Successful Response
     * @throws ApiError
     */
    public static updateNavigationItemApiV1NavigationItemsItemIdPut(
        itemId: number,
        requestBody: NavigationItemUpdate,
    ): CancelablePromise<NavigationItemPublic> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/navigation/items/{item_id}',
            path: {
                'item_id': itemId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 删除指定的导航项
     * 删除当前认证用户拥有的特定导航项。
     * @param itemId 要删除的导航项ID
     * @returns void
     * @throws ApiError
     */
    public static deleteNavigationItemApiV1NavigationItemsItemIdDelete(
        itemId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/navigation/items/{item_id}',
            path: {
                'item_id': itemId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 重新排序指定导航分组下的导航项
     * 根据提供的 ID 列表重新排序指定导航分组下的导航项。
     * 请求体应为 `{"ordered_item_ids": [id1, id2, id3, ...]}`，其中 ID 按新顺序排列。
     * @param groupId 要重新排序导航项的分组ID
     * @param requestBody
     * @returns string Successful Response
     * @throws ApiError
     */
    public static reorderNavigationItemsApiV1NavigationGroupsGroupIdItemsReorderPost(
        groupId: number,
        requestBody: Record<string, Array<number>>,
    ): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/navigation/groups/{group_id}/items/reorder',
            path: {
                'group_id': groupId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
