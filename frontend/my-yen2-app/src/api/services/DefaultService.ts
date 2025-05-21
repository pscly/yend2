/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Debug Echo
     * 一个通用的回显接口，用于调试请求。
     * 返回请求的详细信息，包括方法、URL、头部、客户端IP和接收到的数据。
     * @returns any Successful Response
     * @throws ApiError
     */
    public static debugEchoApiV1DebugEchoPut(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/debug/echo',
        });
    }
    /**
     * Debug Echo
     * 一个通用的回显接口，用于调试请求。
     * 返回请求的详细信息，包括方法、URL、头部、客户端IP和接收到的数据。
     * @returns any Successful Response
     * @throws ApiError
     */
    public static debugEchoApiV1DebugEchoPut1(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/debug/echo',
        });
    }
    /**
     * Debug Echo
     * 一个通用的回显接口，用于调试请求。
     * 返回请求的详细信息，包括方法、URL、头部、客户端IP和接收到的数据。
     * @returns any Successful Response
     * @throws ApiError
     */
    public static debugEchoApiV1DebugEchoPut2(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/debug/echo',
        });
    }
    /**
     * Debug Echo
     * 一个通用的回显接口，用于调试请求。
     * 返回请求的详细信息，包括方法、URL、头部、客户端IP和接收到的数据。
     * @returns any Successful Response
     * @throws ApiError
     */
    public static debugEchoApiV1DebugEchoPut3(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/debug/echo',
        });
    }
    /**
     * Debug Echo
     * 一个通用的回显接口，用于调试请求。
     * 返回请求的详细信息，包括方法、URL、头部、客户端IP和接收到的数据。
     * @returns any Successful Response
     * @throws ApiError
     */
    public static debugEchoApiV1DebugEchoPut4(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/debug/echo',
        });
    }
}
