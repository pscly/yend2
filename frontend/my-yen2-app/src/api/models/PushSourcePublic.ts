/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 公开的推送来源信息 Schema，用于 API 响应。
 * 原始 config 字段将被排除，通过 config_display 提供处理过的版本。
 */
export type PushSourcePublic = {
    /**
     * 推送来源的易记名称
     */
    name: string;
    /**
     * 来源类型 (如 'dingtalk', 'webhook', 'email')
     */
    source_type: string;
    /**
     * 推送来源的描述 (可选)
     */
    description?: (string | null);
    /**
     * 此推送来源是否启用，默认为 True
     */
    is_active?: boolean;
    /**
     * 来源的特定配置 (JSON对象)，例如 webhook URL、API 密钥等
     */
    config?: (Record<string, any> | null);
    id: number;
    created_at: string;
    updated_at: string;
    /**
     * 提供一个用于显示的、可能经过处理的配置版本。
     * 这里可以实现逻辑来过滤掉敏感信息。
     */
    readonly config_display: (Record<string, any> | null);
};

