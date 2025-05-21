/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PushMessagePublic } from '../models/PushMessagePublic';
import type { PushMessageUpdate } from '../models/PushMessageUpdate';
import type { PushSourceCreate } from '../models/PushSourceCreate';
import type { PushSourcePublic } from '../models/PushSourcePublic';
import type { PushSourceUpdate } from '../models/PushSourceUpdate';
import type { PushSubscriptionCreate } from '../models/PushSubscriptionCreate';
import type { PushSubscriptionPublic } from '../models/PushSubscriptionPublic';
import type { PushSubscriptionUpdate } from '../models/PushSubscriptionUpdate';
import type { WebhookMessagePayload } from '../models/WebhookMessagePayload';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PushNotificationsService {
    /**
     *  (管理员) 创建新的推送来源
     * 创建一个新的推送来源。例如，配置一个钉钉机器人或一个通用的 Webhook 接收点。
     * 仅限超级管理员操作。
     * @param requestBody
     * @returns PushSourcePublic Successful Response
     * @throws ApiError
     */
    public static createPushSourceApiV1PushSourcesPost(
        requestBody: PushSourceCreate,
    ): CancelablePromise<PushSourcePublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/push/sources',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (管理员或认证用户) 获取推送来源列表
     * 获取推送来源列表。
     * - 普通认证用户或匿名用户通常只能看到激活的来源。
     * - 管理员可以通过 `only_active=False` 查看所有来源。
     * @param skip
     * @param limit
     * @param onlyActive 仅返回激活的推送来源 (对普通用户默认为True)
     * @returns PushSourcePublic Successful Response
     * @throws ApiError
     */
    public static readPushSourcesApiV1PushSourcesGet(
        skip?: number,
        limit: number = 100,
        onlyActive: boolean = true,
    ): CancelablePromise<Array<PushSourcePublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/push/sources',
            query: {
                'skip': skip,
                'limit': limit,
                'only_active': onlyActive,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (管理员) 获取指定推送来源详情
     * 获取特定推送来源的详细信息。
     * 仅限超级管理员操作（因为可能包含敏感配置的引用）。
     * @param sourceId
     * @returns PushSourcePublic Successful Response
     * @throws ApiError
     */
    public static readPushSourceDetailsApiV1PushSourcesSourceIdGet(
        sourceId: number,
    ): CancelablePromise<PushSourcePublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/push/sources/{source_id}',
            path: {
                'source_id': sourceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (管理员) 更新指定推送来源
     * 更新特定推送来源的信息。
     * 仅限超级管理员操作。
     * @param sourceId
     * @param requestBody
     * @returns PushSourcePublic Successful Response
     * @throws ApiError
     */
    public static updatePushSourceApiV1PushSourcesSourceIdPut(
        sourceId: number,
        requestBody: PushSourceUpdate,
    ): CancelablePromise<PushSourcePublic> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/push/sources/{source_id}',
            path: {
                'source_id': sourceId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (管理员) 删除指定推送来源
     * 删除特定的推送来源。
     * 相关的订阅和（可能）消息也会被级联删除（取决于模型定义）。
     * 仅限超级管理员操作。
     * @param sourceId
     * @returns void
     * @throws ApiError
     */
    public static deletePushSourceApiV1PushSourcesSourceIdDelete(
        sourceId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/push/sources/{source_id}',
            path: {
                'source_id': sourceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 用户订阅推送来源
     * 当前认证用户订阅一个推送来源。
     * 如果用户已订阅该来源，则可能返回错误或更新现有订阅状态。
     * @param requestBody
     * @returns PushSubscriptionPublic Successful Response
     * @throws ApiError
     */
    public static createUserSubscriptionApiV1PushSubscriptionsPost(
        requestBody: PushSubscriptionCreate,
    ): CancelablePromise<PushSubscriptionPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/push/subscriptions',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取当前用户的推送订阅列表
     * 获取当前认证用户的所有推送订阅列表。
     * @param skip
     * @param limit
     * @param onlyActive 仅返回激活的订阅
     * @returns PushSubscriptionPublic Successful Response
     * @throws ApiError
     */
    public static readUserSubscriptionsApiV1PushSubscriptionsGet(
        skip?: number,
        limit: number = 100,
        onlyActive: boolean = false,
    ): CancelablePromise<Array<PushSubscriptionPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/push/subscriptions',
            query: {
                'skip': skip,
                'limit': limit,
                'only_active': onlyActive,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 更新用户的推送订阅
     * 更新当前认证用户的特定推送订阅（例如，启用/禁用，修改用户特定配置）。
     * @param subscriptionId
     * @param requestBody
     * @returns PushSubscriptionPublic Successful Response
     * @throws ApiError
     */
    public static updateUserSubscriptionApiV1PushSubscriptionsSubscriptionIdPut(
        subscriptionId: number,
        requestBody: PushSubscriptionUpdate,
    ): CancelablePromise<PushSubscriptionPublic> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/push/subscriptions/{subscription_id}',
            path: {
                'subscription_id': subscriptionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 用户取消订阅推送来源
     * 当前认证用户取消对特定推送来源的订阅。
     * @param subscriptionId
     * @returns void
     * @throws ApiError
     */
    public static deleteUserSubscriptionApiV1PushSubscriptionsSubscriptionIdDelete(
        subscriptionId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/push/subscriptions/{subscription_id}',
            path: {
                'subscription_id': subscriptionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取当前用户的推送消息列表
     * 获取当前认证用户收到的推送消息列表，支持分页和筛选。
     * @param skip
     * @param limit
     * @param sourceId 按来源ID筛选
     * @param status 按消息状态筛选 (e.g., 'unread', 'read')
     * @param unreadOnly 仅返回未读消息
     * @returns PushMessagePublic Successful Response
     * @throws ApiError
     */
    public static readUserPushMessagesApiV1PushMessagesGet(
        skip?: number,
        limit: number = 50,
        sourceId?: (number | null),
        status?: (string | null),
        unreadOnly?: (boolean | null),
    ): CancelablePromise<Array<PushMessagePublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/push/messages',
            query: {
                'skip': skip,
                'limit': limit,
                'source_id': sourceId,
                'status': status,
                'unread_only': unreadOnly,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 更新用户消息的状态 (例如，标记为已读)
     * 更新当前认证用户拥有的特定消息的状态。
     * 主要用于将消息标记为“已读”或“已归档”。
     * @param messageId
     * @param requestBody
     * @returns PushMessagePublic Successful Response
     * @throws ApiError
     */
    public static updateUserMessageStatusApiV1PushMessagesMessageIdStatusPut(
        messageId: number,
        requestBody: PushMessageUpdate,
    ): CancelablePromise<PushMessagePublic> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/push/messages/{message_id}/status',
            path: {
                'message_id': messageId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 将用户的所有（或特定来源的）未读消息标记为已读
     * 将当前认证用户的所有未读消息（或特定来源的未读消息）标记为“已读”。
     * 返回受影响的消息数量。
     * @param sourceId 可选：仅标记特定来源的未读消息
     * @returns any Successful Response
     * @throws ApiError
     */
    public static markAllUserMessagesAsReadApiV1PushMessagesMarkAllReadPost(
        sourceId?: (number | null),
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/push/messages/mark-all-read',
            query: {
                'source_id': sourceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (Webhook) 接收外部系统推送来的消息
     * 用于接收来自已配置的外部推送来源（例如自定义 Webhook、第三方服务回调）的消息。
     * 系统会根据 `source_identifier` 找到对应的 `PushSource`，
     * 然后将消息分发给所有订阅了该来源的活跃用户。
     *
     * **安全要求**:
     * - 必须提供有效的 X-Webhook-Secret 头，与推送来源配置中的secret匹配
     * - 请求IP必须在允许列表中（如果来源配置了IP白名单）
     * - 某些来源可能需要验证签名（取决于source_type）
     * @param sourceIdentifier 推送来源的唯一标识符
     * @param requestBody
     * @param xWebhookSecret
     * @returns any Successful Response
     * @throws ApiError
     */
    public static receiveWebhookMessageApiV1PushWebhooksIngressSourceIdentifierPost(
        sourceIdentifier: string,
        requestBody: WebhookMessagePayload,
        xWebhookSecret?: (string | null),
    ): CancelablePromise<Record<string, (string | number)>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/push/webhooks/ingress/{source_identifier}',
            path: {
                'source_identifier': sourceIdentifier,
            },
            headers: {
                'X-Webhook-Secret': xWebhookSecret,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
