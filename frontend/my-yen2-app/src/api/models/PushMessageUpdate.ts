/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 更新推送消息时使用的 Schema (例如，更新状态)。
 */
export type PushMessageUpdate = {
    /**
     * 消息状态 (如 'read', 'archived')
     */
    status?: (string | null);
    /**
     * 用户阅读消息的时间
     */
    read_at?: (string | null);
};

