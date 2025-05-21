/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AnonymousPushService {
    /**
     * Anonymous Push
     * 匿名推送消息接口，支持GET和POST请求。
     *
     * - GET请求：通过URL参数接收 bt(标题) 和 content(内容)
     * - POST请求：支持表单数据和JSON格式，接收 bt(标题) 和 content(内容)
     *
     * 响应始终包含：
     * - 当前时间（格式化为易读的日期时间字符串）
     * - 当前请求的完整URL
     * - 请求中的所有参数（作为字典）
     *
     * 示例：
     * - GET: /d1?bt=标题&content=内容
     * - POST (表单): /d1 (表单数据: bt=标题&content=内容)
     * - POST (JSON): /d1 (JSON数据: {"bt": "标题", "content": "内容"})
     * @returns any Successful Response
     * @throws ApiError
     */
    public static anonymousPushD1Post(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/d1',
        });
    }
    /**
     * Anonymous Push
     * 匿名推送消息接口，支持GET和POST请求。
     *
     * - GET请求：通过URL参数接收 bt(标题) 和 content(内容)
     * - POST请求：支持表单数据和JSON格式，接收 bt(标题) 和 content(内容)
     *
     * 响应始终包含：
     * - 当前时间（格式化为易读的日期时间字符串）
     * - 当前请求的完整URL
     * - 请求中的所有参数（作为字典）
     *
     * 示例：
     * - GET: /d1?bt=标题&content=内容
     * - POST (表单): /d1 (表单数据: bt=标题&content=内容)
     * - POST (JSON): /d1 (JSON数据: {"bt": "标题", "content": "内容"})
     * @returns any Successful Response
     * @throws ApiError
     */
    public static anonymousPushD1Post1(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/d1',
        });
    }
}
