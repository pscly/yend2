/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 创建新推送来源时使用的 Schema。
 */
export type PushSourceCreate = {
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
};

