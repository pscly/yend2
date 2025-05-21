/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 更新推送来源时使用的 Schema。所有字段可选。
 */
export type PushSourceUpdate = {
    name?: (string | null);
    source_type?: (string | null);
    description?: (string | null);
    is_active?: (boolean | null);
    /**
     * 更新来源的特定配置 (JSON对象)
     */
    config?: (Record<string, any> | null);
};

