/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 更新用户信息时使用的 Schema。
 * 所有字段都是可选的，因为用户可能只更新部分信息。
 */
export type UserUpdate = {
    /**
     * 新的用户名。
     */
    username?: (string | null);
    /**
     * 新的电子邮箱。
     */
    email?: (string | null);
    /**
     * 新的用户密码（如果需要修改）。
     */
    password?: (string | null);
    /**
     * 更新账户激活状态。
     */
    is_active?: (boolean | null);
    /**
     * 更新用户是否为超级管理员。
     */
    is_superuser?: (boolean | null);
};

