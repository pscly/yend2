/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 更新用户推送订阅时使用的 Schema。
 * 通常只允许更新 is_active 和 user_specific_config。
 */
export type PushSubscriptionUpdate = {
    is_active?: (boolean | null);
    user_specific_config?: (Record<string, any> | null);
};

