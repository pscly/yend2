/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserCreate } from '../models/UserCreate';
import type { UserPublic } from '../models/UserPublic';
import type { UserUpdate } from '../models/UserUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UsersService {
    /**
     * 获取当前用户信息
     * 获取当前已认证用户（通过 Access Token）的公开信息。
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static readUserMeApiV1UsersMeGet(): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me',
        });
    }
    /**
     * 更新当前用户信息
     * 更新当前已认证用户的信息。
     * 用户只能更新自己的信息。
     * @param requestBody
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static updateUserMeApiV1UsersMePut(
        requestBody: UserUpdate,
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/users/me',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 用户注册
     * 创建新用户账户（开放注册）。
     * 如果用户名或邮箱已存在，将返回错误。
     * @param requestBody
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static registerNewUserApiV1UsersRegisterPost(
        requestBody: UserCreate,
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/users/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (管理员) 获取用户列表
     * 获取用户列表 (分页)。
     * 仅限超级管理员访问。
     * @param skip
     * @param limit
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static readUsersListApiV1UsersGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<UserPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (管理员) 获取指定用户信息
     * 通过用户 ID 获取特定用户的信息。
     * 仅限超级管理员访问。
     * @param userId
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static readUserByIdApiV1UsersUserIdGet(
        userId: number,
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (管理员) 更新指定用户信息
     * (管理员) 更新指定 ID 用户的信息。
     * 需要谨慎处理密码更新逻辑。
     * @param userId
     * @param requestBody
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static updateUserByIdAsAdminApiV1UsersUserIdPut(
        userId: number,
        requestBody: UserUpdate,
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/users/{user_id}',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     *  (管理员) 删除指定用户
     * (管理员) 删除指定 ID 的用户。
     * 这是一个危险操作，请谨慎使用。
     * @param userId
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static deleteUserByIdAsAdminApiV1UsersUserIdDelete(
        userId: number,
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/users/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
