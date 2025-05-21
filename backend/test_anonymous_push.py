#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试匿名推送接口的脚本
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_get_request():
    """测试GET请求"""
    print("\n=== 测试GET请求 ===")

    # 构建URL参数
    params = {
        "bt": "GET测试标题",
        "content": "这是通过GET请求发送的测试内容"
    }

    # 发送GET请求
    response = requests.get(f"{BASE_URL}/d1", params=params)

    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    # 验证响应中包含必要的字段
    result = response.json()
    return (response.status_code == 200 and
            "timestamp" in result and
            "url" in result and
            "params" in result and
            "success" in result)

def test_post_form_request():
    """测试POST表单请求"""
    print("\n=== 测试POST表单请求 ===")

    # 构建表单数据
    data = {
        "bt": "POST表单测试标题",
        "content": "这是通过POST表单发送的测试内容"
    }

    # 发送POST表单请求
    response = requests.post(f"{BASE_URL}/d1", data=data)

    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    # 验证响应中包含必要的字段
    result = response.json()
    return (response.status_code == 200 and
            "timestamp" in result and
            "url" in result and
            "params" in result and
            "success" in result)

def test_post_json_request():
    """测试POST JSON请求"""
    print("\n=== 测试POST JSON请求 ===")

    # 构建JSON数据
    data = {
        "bt": "POST JSON测试标题",
        "content": "这是通过POST JSON发送的测试内容"
    }

    # 发送POST JSON请求
    response = requests.post(
        f"{BASE_URL}/d1",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    # 验证响应中包含必要的字段
    result = response.json()
    return (response.status_code == 200 and
            "timestamp" in result and
            "url" in result and
            "params" in result and
            "success" in result)

def test_missing_content():
    """测试缺少content参数的情况"""
    print("\n=== 测试缺少content参数 ===")

    # 构建不完整的数据
    params = {
        "bt": "缺少content的测试"
    }

    # 发送GET请求
    response = requests.get(f"{BASE_URL}/d1", params=params)

    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    # 验证响应中包含必要的字段，但不应该有success字段
    result = response.json()
    return (response.status_code == 200 and
            "timestamp" in result and
            "url" in result and
            "params" in result and
            "has_title" in result and
            "has_content" in result and
            "success" not in result)

def test_no_params():
    """测试没有任何参数的情况"""
    print("\n=== 测试没有任何参数 ===")

    # 发送GET请求，不带任何参数
    response = requests.get(f"{BASE_URL}/d1")

    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    # 验证响应中包含必要的字段，且有"没有参数"的消息
    result = response.json()
    return (response.status_code == 200 and
            "timestamp" in result and
            "url" in result and
            "params" in result and
            "message" in result and
            "没有参数" in result["message"])

def test_only_content():
    """测试只有content参数的情况"""
    print("\n=== 测试只有content参数 ===")

    # 构建只有content的数据
    params = {
        "content": "只有内容没有标题的测试"
    }

    # 发送GET请求
    response = requests.get(f"{BASE_URL}/d1", params=params)

    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    # 验证响应中包含必要的字段
    result = response.json()
    return (response.status_code == 200 and
            "timestamp" in result and
            "url" in result and
            "params" in result and
            "has_title" in result and
            "has_content" in result and
            result["has_title"] is False and
            result["has_content"] is True)

def main():
    """主函数"""
    print("开始测试匿名推送接口...")

    # 运行所有测试
    tests = [
        test_get_request,
        test_post_form_request,
        test_post_json_request,
        test_missing_content,
        test_no_params,
        test_only_content
    ]

    success_count = 0
    for test_func in tests:
        try:
            if test_func():
                success_count += 1
                print(f"✅ {test_func.__name__} 测试通过")
            else:
                print(f"❌ {test_func.__name__} 测试失败")
        except Exception as e:
            print(f"❌ {test_func.__name__} 测试出错: {str(e)}")

    print(f"\n测试完成: {success_count}/{len(tests)} 个测试通过")

    return 0 if success_count == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())
