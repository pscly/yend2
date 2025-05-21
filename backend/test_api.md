# test_api

## toc

1. [test\_api](#test_api)
    1. [toc](#toc)
    2. [测试命令1](#测试命令1)

## 测试命令1

基本说明:

    BASE_URL: 我将使用 http://127.0.0.1:8000/api/v1 作为基础 URL。请根据你的实际配置调整。

    ACCESS_TOKEN: 很多请求需要认证。你需要先通过登录获取一个 access_token，然后将其用在后续请求的 Authorization 头部。我会标记需要 token 的请求。

    Content-Type: 对于 POST 和 PUT 请求，如果发送 JSON 数据，确保设置 Content-Type: application/json。对于登录接口，Content-Type 是 application/x-www-form-urlencoded。

    占位符: 我会使用像 {USER_ID}, {GROUP_ID}, {ITEM_ID}, {SOURCE_ID}, {SUB_ID}, {MSG_ID} 这样的占位符。你需要用实际从 API 响应中获取到的 ID 替换它们。

    JSON 数据: curl 命令中的 -d 或 --data 参数后的 JSON 数据需要是单行，或者使用文件 (-d @file.json)。在 APIPost 中，你可以直接在 Body -> raw -> JSON 中输入格式化的 JSON。

零、准备工作

    确保你的 FastAPI 应用正在运行 (uvicorn app.main:app --reload)。

    准备一个 API 测试工具，如 APIPost。

一、用户认证与管理模块 (/auth 和 /users)

1. 用户注册 (如果开放)

    Endpoint: POST /users/register

    curl 命令:
    curl -X POST 'http://127.0.0.1:8000/api/v1/users/register' -H 'Content-Type: application/json' -d '{ "username": "testuser1", "email": "testuser1@example.com", "password": "StrongPassword123" }'

    预期: 201 Created，返回新用户信息。记下用户名和密码。

    再注册一个用户 testuser2:
    curl -X POST 'http://127.0.0.1:8000/api/v1/users/register' -H 'Content-Type: application/json' -d '{ "username": "testuser2", "email": "testuser2@example.com", "password": "AnotherPassword456" }' 

2. 用户登录 (获取 Token)

    Endpoint: POST /auth/login

    curl 命令 (for testuser1):
    curl -X POST 'http://127.0.0.1:8000/api/v1/auth/login' -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=testuser1&password=StrongPassword123'

    预期: 200 OK，返回 access_token 和 token_type。

    操作: 复制 access_token 的值。后续需要认证的请求会用到它。为了方便，我们称其为 <<USER1_TOKEN>>。

    登录 testuser2 并获取 USER2_TOKEN (如果需要测试多用户场景)。

3. 获取当前用户信息

    Endpoint: GET /users/me

    需要 Token: <<USER1_TOKEN>>

    curl 命令:
    curl -X GET 'http://127.0.0.1:8000/api/v1/users/me' -H 'Authorization: Bearer <<USER1_TOKEN>>'

    预期: 200 OK，返回 testuser1 的信息。

4. 更新当前用户信息

    Endpoint: PUT /users/me

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (例如，更新邮箱):
    curl -X PUT 'http://127.0.0.1:8000/api/v1/users/me' -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d '{ "email": "testuser1_updated@example.com" }'

    预期: 200 OK，返回更新后的用户信息。

5. (管理员) 获取用户列表 (假设你已创建一个超级用户并用其 token ADMIN_TOKEN)

    Endpoint: GET /users/

    需要 Token: ADMIN_TOKEN

    curl 命令:
    curl -X GET 'http://127.0.0.1:8000/api/v1/users/' -H 'Authorization: Bearer ADMIN_TOKEN'

    预期: 200 OK，返回用户列表。

二、导航管理模块 (/navigation)

假设我们使用 testuser1 的 <<USER1_TOKEN>> 进行操作。

1. 创建导航分组

    Endpoint: POST /navigation/groups

    需要 Token: <<USER1_TOKEN>>

    curl 命令:
    curl -X POST 'http://127.0.0.1:8000/api/v1/navigation/groups' -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d '{ "name": "工作相关", "description": "常用的工作网站和工具", "order_index": 0 }'

    预期: 201 Created，返回新创建的分组信息。记下返回的 id，例如 GROUP1_ID。

    再创建一个分组:
    curl -X POST 'http://127.0.0.1:8000/api/v1/navigation/groups' -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d '{ "name": "学习资源", "order_index": 1 }'
    记下其 id，例如 GROUP2_ID。

2. 获取用户的所有导航分组

    Endpoint: GET /navigation/groups

    需要 Token: <<USER1_TOKEN>>

    curl 命令:
    curl -X GET 'http://127.0.0.1:8000/api/v1/navigation/groups' -H 'Authorization: Bearer <<USER1_TOKEN>>'

    预期: 200 OK，返回 testuser1 创建的导航分组列表。

3. 创建导航项 (在 GROUP1_ID 下)

    Endpoint: POST /navigation/groups/{group_id}/items

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (将 {GROUP1_ID} 替换为实际ID):
    curl -X POST "http://127.0.0.1:8000/api/v1/navigation/groups/${GROUP1_ID}/items" -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d '{ "title": "公司内部GitLab", "url": "https://gitlab.company.com", "order_index": 0 }'

    预期: 201 Created，返回新创建的导航项信息。记下其 id，例如 ITEM1_ID。

    再创建一个导航项 (在 GROUP1_ID 下):
    curl -X POST "http://127.0.0.1:8000/api/v1/navigation/groups/${GROUP1_ID}/items" -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d '{ "title": "Jira看板", "url": "https://jira.company.com", "order_index": 1 }'
    记下其 id，例如 ITEM2_ID。

4. 获取指定导航分组及其项

    Endpoint: GET /navigation/groups/{group_id}

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (将 {GROUP1_ID} 替换为实际ID):
    curl -X GET "http://127.0.0.1:8000/api/v1/navigation/groups/${GROUP1_ID}" -H 'Authorization: Bearer <<USER1_TOKEN>>'

    预期: 200 OK，返回 GROUP1_ID 的详细信息及其下的 items 列表。

5. 更新导航项

    Endpoint: PUT /navigation/items/{item_id}

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (将 {ITEM1_ID} 替换为实际ID，例如更新标题):
    curl -X PUT "http://127.0.0.1:8000/api/v1/navigation/items/${ITEM1_ID}" -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d '{ "title": "公司GitLab (代码库)" }'

    预期: 200 OK，返回更新后的导航项信息。

6. 重新排序导航项 (在 GROUP1_ID 下)

    Endpoint: POST /navigation/groups/{group_id}/items/reorder

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (将 {GROUP1_ID}, {ITEM1_ID}, {ITEM2_ID} 替换为实际ID，假设交换顺序):
    curl -X POST "http://127.0.0.1:8000/api/v1/navigation/groups/${GROUP1_ID}/items/reorder" -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d "{ \"ordered_item_ids\": [${ITEM2_ID}, ${ITEM1_ID}] }"
    注意 ordered_item_ids 的值是一个 JSON 数组。

    预期: 200 OK，返回成功消息。再次获取该分组查看排序是否生效。

7. 删除导航项

    Endpoint: DELETE /navigation/items/{item_id}

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (将 {ITEM1_ID} 替换为实际ID):
    curl -X DELETE "http://127.0.0.1:8000/api/v1/navigation/items/${ITEM1_ID}" -H 'Authorization: Bearer <<USER1_TOKEN>>'

    预期: 204 No Content。

8. 删除导航分组

    Endpoint: DELETE /navigation/groups/{group_id}

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (将 {GROUP1_ID} 替换为实际ID):
    curl -X DELETE "http://127.0.0.1:8000/api/v1/navigation/groups/${GROUP1_ID}" -H 'Authorization: Bearer <<USER1_TOKEN>>'

    预期: 204 No Content。

三、推送管理模块 (/push)

假设你已有一个超级用户并使用其 token ADMIN_TOKEN，以及普通用户 testuser1 的 <<USER1_TOKEN>>。

1. (管理员) 创建推送来源

    Endpoint: POST /push/sources

    需要 Token: ADMIN_TOKEN

    curl 命令:
    curl -X POST 'http://127.0.0.1:8000/api/v1/push/sources' -H 'Content-Type: application/json' -H 'Authorization: Bearer ADMIN_TOKEN' -d '{ "name": "每日新闻推送", "source_type": "webhook", "description": "通过Webhook接收每日新闻摘要", "is_active": true, "config": {"secret": "mywebhooksecret123"} }'

    预期: 201 Created，返回新来源信息。记下 id，例如 SOURCE1_ID。

2. (用户) 获取可订阅的推送来源列表

    Endpoint: GET /push/sources

    需要 Token: <<USER1_TOKEN>> (或匿名，取决于你的实现)

    curl 命令:
    curl -X GET 'http://127.0.0.1:8000/api/v1/push/sources?only_active=true' -H 'Authorization: Bearer <<USER1_TOKEN>>'

    预期: 200 OK，返回激活的推送来源列表。

3. (用户) 订阅推送来源

    Endpoint: POST /push/subscriptions

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (将 {SOURCE1_ID} 替换为实际ID):
    curl -X POST 'http://127.0.0.1:8000/api/v1/push/subscriptions' -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d "{ \"source_id\": ${SOURCE1_ID}, \"is_active\": true }"

    预期: 201 Created，返回新的订阅信息。记下 id，例如 SUB1_ID。

4. (Webhook) 模拟外部消息推送到来源

    Endpoint: POST /push/webhooks/ingress/{source_identifier}

    注意: 这里的 {source_identifier} 我们用的是 PushSource 的 id (SOURCE1_ID)。这个端点不需要用户 token，但可能需要你实现的 Webhook 密钥验证。

    curl 命令 (将 {SOURCE1_ID} 替换为实际ID):
    ```bash
    curl -X POST
    "http://127.0.0.1:8000/api/v1/push/webhooks/ingress/${SOURCE1_ID}"
    -H 'Content-Type: application/json' \
    -H 'X-Webhook-Secret: mywebhooksecret123' # 如果你实现了密钥验证

    -d '{
    "source_identifier": "'"${SOURCE1_ID}"'",
    "title": "今日头条新闻",
    "content": "发生了一些有趣的事情...",
    "content_type": "text/plain"
    }'
    ```

    预期: 202 Accepted。

5. (用户) 获取收到的推送消息

    Endpoint: GET /push/messages

    需要 Token: <<USER1_TOKEN>>

    curl 命令:
    curl -X GET 'http://127.0.0.1:8000/api/v1/push/messages' -H 'Authorization: Bearer <<USER1_TOKEN>>'

    预期: 200 OK，返回 testuser1 收到的消息列表，应包含刚才通过 Webhook 发送的消息。记下某条消息的 id，例如 MSG1_ID。

6. (用户) 将消息标记为已读

    Endpoint: PUT /push/messages/{message_id}/status

    需要 Token: <<USER1_TOKEN>>

    curl 命令 (将 {MSG1_ID} 替换为实际ID):
    curl -X PUT "http://127.0.0.1:8000/api/v1/push/messages/${MSG1_ID}/status" -H 'Content-Type: application/json' -H 'Authorization: Bearer <<USER1_TOKEN>>' -d '{ "status": "read" }'

    预期: 200 OK，返回更新后的消息信息，其 status 应为 read，read_at 时间已设置。

7. (用户) 将所有未读消息标记为已读
* Endpoint: POST /push/messages/mark-all-read
* 需要 Token: <<USER1_TOKEN>>
* curl 命令:
curl -X POST 'http://127.0.0.1:8000/api/v1/push/messages/mark-all-read' -H 'Authorization: Bearer <<USER1_TOKEN>>'
* 预期: 200 OK，返回受影响的消息数量。
