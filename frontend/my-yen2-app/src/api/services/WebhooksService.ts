/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WebhookMessagePayload } from '../models/WebhookMessagePayload';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WebhooksService {
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
