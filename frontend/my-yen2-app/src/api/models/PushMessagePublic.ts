/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PushSourcePublic } from './PushSourcePublic';
/**
 * 公开的推送消息信息 Schema，用于 API 响应。
 */
export type PushMessagePublic = {
    /**
     * 消息标题 (可选)
     */
    title?: (string | null);
    /**
     * 消息主体内容
     */
    content: string;
    /**
     * 内容类型 (如 'text/plain', 'text/markdown')
     */
    content_type?: string;
    id: number;
    user_id?: (number | null);
    source_id?: (number | null);
    status: string;
    received_at: string;
    sent_at?: (string | null);
    read_at?: (string | null);
    created_at: string;
    updated_at: string;
    source?: (PushSourcePublic | null);
};

