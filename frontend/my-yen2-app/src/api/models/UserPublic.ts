/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 公开的用户信息 Schema，用于 API 响应。
 * 不包含密码等敏感字段。
 */
export type UserPublic = {
    /**
     * 用户名，3-100个字符，只能包含字母、数字和下划线。
     */
    username: string;
    /**
     * 用户的电子邮箱，必须是有效的邮箱格式。
     */
    email?: (string | null);
    /**
     * 账户是否激活，默认为 True。
     */
    is_active?: (boolean | null);
    /**
     * 是否为超级管理员，默认为 False。
     */
    is_superuser?: boolean;
    id: number;
    created_at: string;
    updated_at: string;
};

