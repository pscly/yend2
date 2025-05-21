/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PushSourcePublic } from './PushSourcePublic';
/**
 * 公开的用户推送订阅信息 Schema，用于 API 响应。
 */
export type PushSubscriptionPublic = {
    /**
     * 用户是否希望接收此订阅的推送，默认为 True
     */
    is_active?: boolean;
    /**
     * 用户针对此订阅的特定配置 (JSON对象)
     */
    user_specific_config?: (Record<string, any> | null);
    id: number;
    user_id: number;
    source_id: number;
    created_at: string;
    updated_at: string;
    source?: (PushSourcePublic | null);
};

