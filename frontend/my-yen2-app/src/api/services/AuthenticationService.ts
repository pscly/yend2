/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_for_access_token_api_v1_auth_login_post } from '../models/Body_login_for_access_token_api_v1_auth_login_post';
import type { Token } from '../models/Token';
import type { UserPublic } from '../models/UserPublic';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthenticationService {
    /**
     * 用户登录获取访问令牌
     * OAuth2兼容的登录接口，用于获取访问令牌 (Access Token)。
     *
     * 客户端应使用 `application/x-www-form-urlencoded` 类型提交 `username` 和 `password`。
     * 成功后返回包含 `access_token` 和 `token_type` 的 JSON 对象。
     * @param formData
     * @returns Token Successful Response
     * @throws ApiError
     */
    public static loginForAccessTokenApiV1AuthLoginPost(
        formData: Body_login_for_access_token_api_v1_auth_login_post,
    ): CancelablePromise<Token> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 测试访问令牌有效性
     * 一个受保护的端点，用于测试客户端提供的 Access Token 是否有效。
     * 如果 token 有效且用户已激活，则返回当前用户的信息。
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static testTokenApiV1AuthTestTokenPost(): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/test-token',
        });
    }
}
