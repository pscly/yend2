/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 创建新用户时使用的 Schema。
 * 继承自 UserBase，并添加了密码字段。
 */
export type UserCreate = {
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
    /**
     * 用户密码，至少8个字符。
     */
    password: string;
};

