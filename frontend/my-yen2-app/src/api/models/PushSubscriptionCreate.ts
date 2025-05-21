/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 用户创建新推送订阅时使用的 Schema。
 * 需要提供要订阅的 source_id。
 */
export type PushSubscriptionCreate = {
    /**
     * 用户是否希望接收此订阅的推送，默认为 True
     */
    is_active?: boolean;
    /**
     * 用户针对此订阅的特定配置 (JSON对象)
     */
    user_specific_config?: (Record<string, any> | null);
    source_id: number;
};

