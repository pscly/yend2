# yend2 - 项目 README

## toc

1. [yend2 - 项目 README](#yend2---项目-readme)
    1. [toc](#toc)
    2. [1. 项目简介](#1-项目简介)
    3. [2. 技术栈](#2-技术栈)
    4. [3. 核心功能规划](#3-核心功能规划)
        1. [3.1. 导航页 (用户自定义)](#31-导航页-用户自定义)
        2. [3.2. 多用户推送管理](#32-多用户推送管理)
        3. [3.3. 多端共联 (远期规划)](#33-多端共联-远期规划)
    5. [4. API 接口设计 (初步)](#4-api-接口设计-初步)
        1. [4.1. 通用约定](#41-通用约定)
        2. [4.2. 认证接口 (`/api/v1/auth`)](#42-认证接口-apiv1auth)
        3. [4.3. 导航页接口 (`/api/v1/navigation`)](#43-导航页接口-apiv1navigation)
        4. [4.4. 推送管理接口 (`/api/v1/push`)](#44-推送管理接口-apiv1push)
        5. [4.5. 其他接口](#45-其他接口)
    6. [5. 配置文件说明](#5-配置文件说明)
    7. [6. 项目目录结构](#6-项目目录结构)
    8. [7. 开发环境搭建与运行](#7-开发环境搭建与运行)
        1. [7.1. 后端 (FastAPI)](#71-后端-fastapi)
        2. [7.2. 前端 (Vue3 + UniApp)](#72-前端-vue3--uniapp)
    9. [剩余问题](#剩余问题)

## 1. 项目简介

`yend2` 是一个基于原有项目 (`yend`) 进行完整重构的现代化 Web 应用。旨在提供一个高度可定制的个人导航中心和高效的多源消息推送管理平台。项目采用前后端分离架构。

## 2. 技术栈

*   **后端:** FastAPI (Python 3.12+)
    *   ORM: SQLAlchemy (支持 PostgreSQL, MySQL, SQLite, Oracle, MSSQL 等多种数据库)
    *   异步支持: `async/await`
    *   数据校验: Pydantic
    *   任务队列: Celery (可选, 用于处理耗时推送任务)
*   **前端:** Vue 3 + UniApp
    *   UI 框架: (例如 Element Plus for Web, uView for UniApp - 请根据你的选择填写)
    *   状态管理: Pinia
    *   打包工具: Vite
*   **数据库:** PostgreSQL (首选推荐, 但 SQLAlchemy 保证了灵活性)
*   **配置管理:** `.env` 文件

## 3. 核心功能规划

### 3.1. 导航页 (用户自定义)

*   **目标:** 提供一个类似浏览器书签或快捷导航的页面，允许用户高度自定义。
*   **[✓] 功能点:**
    *   [ ] **用户账户系统:** 支持用户注册、登录、个人信息管理。导航数据与用户账户绑定。
    *   [ ] **链接管理:**
        *   [ ] 添加、编辑、删除自定义链接。
        *   [ ] 链接可包含：标题、URL、图标 (可选，可自动抓取 favicon 或用户上传)、描述。
        *   [ ] 链接可拖拽排序。
    *   [ ] **分组/分类管理:**
        *   [ ] 用户可以创建链接分组 (如 "工作常用", "学习资源", "娱乐影音")。
        *   [ ] 链接可以归属于不同分组。
        *   [ ] 分组可拖拽排序。
    *   [ ] **外观自定义 (可选):**
        *   [ ] 主题颜色选择。
        *   [ ] 背景图片/颜色设置。
    *   [ ] **搜索功能:** 快速搜索已添加的链接或分组。
    *   [ ] **数据导入/导出 (可选):** 支持从浏览器书签或其他格式导入，或导出为特定格式。
*   **[?] 待考虑:**
    *   **浏览器插件:** 未来可以开发浏览器插件，实现快速添加当前页面到导航页，或者作为新标签页的默认页面。

### 3.2. 多用户推送管理

*   **目标:** 集中管理来自不同渠道的推送消息，并能有效地将这些消息推送给指定的用户或用户组。
*   **[✓] 功能点:**
    *   [ ] **推送来源管理 (Source/Channel):**
        *   [ ] 管理员可配置不同的推送来源，例如：微信公众号、企业微信、钉钉机器人、邮件、自定义 Webhook 等。
        *   [ ] 每个来源有其特定的配置参数 (如 AppID, Secret, Webhook URL)。
        *   [ ] 来源可启用/禁用。
    *   [ ] **用户与推送目标绑定:**
        *   [ ] 用户可以选择性订阅/绑定自己关心的推送来源或具体的推送服务账号 (例如，绑定自己的钉钉机器人)。
    *   [ ] **消息接收与存储:**
        *   [ ] 系统提供统一的入口 (如 Webhook) 接收来自各来源的消息。
        *   [ ] 消息持久化存储，包含：来源、内容、时间戳、目标用户(可选)、状态 (如 未读/已读) 等。
    *   [ ] **消息查看与管理:**
        *   [ ] 用户可以查看自己的历史推送消息。
        *   [ ] 支持按来源分类查看。
        *   [ ] 支持按时间、关键词搜索消息。
        *   [ ] 支持标记消息为已读/未读。
        *   [ ] "流线型" 界面：指界面设计简洁、直观、易于操作，能够清晰展示消息流。
    *   [ ] **消息推送 (可选，如果系统也负责转发):**
        *   [ ] 如果系统不仅仅是收集，还需要将消息主动推给用户的其他终端 (如通过邮件、APP通知)，则需要推送逻辑。
        *   [ ] (否则，此功能主要是指用户在 `yend2` 平台上查看聚合后的消息)
*   **[?] 待考虑:**
    *   **推送模板:** 定义推送消息的格式模板。
    *   **推送策略:** 例如失败重试、定时推送等。

需要添加一个接口，支持匿名推送消息

具体 接口 同时支持 get 和 post ，post支持 表单模式和json格式 (反正把所有的数据内容都合并为一个字典，接收参数是 bt(标题)  content(详细内容,  然后通过一个单独的推送方法进行推送(这个推送方案只是这个接口使用，)))

host/d1

例如

127.0.0.1:8000/d1?bt=1&content=12345



### 3.3. 多端共联 (远期规划)

*   **目标:** 提升用户在不同网络环境下访问应用的体验，特别是针对资源加载速度。
*   **[✓] 功能点 (概念):**
    *   [ ] **节点测速:** 客户端 (JS) 启动时，或在特定时机，向预设的多个服务器节点发送轻量级请求，测试连接延迟和带宽。
    *   [ ] **动态资源切换:** 根据测速结果，客户端动态地将静态资源 (如图片、JS、CSS) 的基础 URL 切换到最优的服务器节点。
    *   [ ] **API 请求路由 (更复杂):** 如果 API 也有多节点部署，可以考虑将 API 请求也导向最优节点，但这需要后端架构支持。
*   **说明:** 此功能较为复杂，依赖于多服务器部署，可以作为远期优化目标。

## 4. API 接口设计 (初步)

### 4.1. 通用约定

*   **Base URL:** `/api/v1` (推荐版本化)
*   **请求格式:** JSON
*   **响应格式:** JSON
    ```json
    {
        "code": 0, // 0 表示成功，其他表示错误代码
        "message": "success", // 成功或错误信息
        "data": {} // 响应数据
    }
    ```
*   **认证:** JWT (JSON Web Tokens) 将用于保护需要授权的接口。Token 通过 `Authorization: Bearer <token>` HTTP 头部传递。
*   **命名:** 接口路径使用 `kebab-case` (短横线连接)。

### 4.2. 认证接口 (`/api/v1/auth`)

*   `POST /api/v1/auth/register`: 用户注册
    *   请求体: `{ "username": "user", "password": "pwd", "email": "user@example.com" }`
    *   响应: 成功信息或错误信息。
*   `POST /api/v1/auth/login`: 用户登录
    *   请求体: `{ "username": "user", "password": "pwd" }`
    *   响应: `{ "access_token": "your_jwt_token", "token_type": "bearer" }`
*   `GET /api/v1/auth/me`: 获取当前用户信息 (需认证)
    *   响应: 用户信息对象。

### 4.3. 导航页接口 (`/api/v1/navigation`)

*   `GET /api/v1/navigation/groups`: 获取当前用户的所有导航分组 (需认证)
    *   响应: 分组列表 `[{ "id": 1, "name": "工作", "order": 0, "items": [...] }]`
*   `POST /api/v1/navigation/groups`: 创建新导航分组 (需认证)
    *   请求体: `{ "name": "新分组" }`
    *   响应: 新创建的分组对象。
*   `PUT /api/v1/navigation/groups/{group_id}`: 更新导航分组信息 (名称、排序) (需认证)
*   `DELETE /api/v1/navigation/groups/{group_id}`: 删除导航分组 (需认证)
*   `GET /api/v1/navigation/items?group_id={group_id}`: 获取指定分组下的所有导航项 (需认证)
*   `POST /api/v1/navigation/items`: 创建新导航项 (需认证)
    *   请求体: `{ "group_id": 1, "title": "Google", "url": "https://google.com", "icon": "url_to_icon" }`
*   `PUT /api/v1/navigation/items/{item_id}`: 更新导航项信息 (需认证)
*   `DELETE /api/v1/navigation/items/{item_id}`: 删除导航项 (需认证)
*   `POST /api/v1/navigation/reorder`: 更新分组或导航项的排序 (需认证)
    *   请求体: `[{ "id": 1, "order": 0, "type": "group/item" }, ...]`

### 4.4. 推送管理接口 (`/api/v1/push`)

*   **管理端接口 (管理员权限):**
    *   `GET /api/v1/push/sources`: 获取所有推送来源配置。
    *   `POST /api/v1/push/sources`: 添加新的推送来源。
    *   `PUT /api/v1/push/sources/{source_id}`: 修改推送来源配置。
    *   `DELETE /api/v1/push/sources/{source_id}`: 删除推送来源。
*   **用户端接口 (需认证):**
    *   `GET /api/v1/push/user-subscriptions`: 获取用户已订阅的推送来源/服务。
    *   `POST /api/v1/push/user-subscriptions`: 用户订阅/绑定新的推送服务。
    *   `DELETE /api/v1/push/user-subscriptions/{subscription_id}`: 用户取消订阅。
    *   `GET /api/v1/push/messages`: 获取用户的推送消息列表 (支持分页、按来源筛选、按时间排序)。
        *   查询参数: `?page=1&limit=20&source_id=1&status=unread`
    *   `GET /api/v1/push/messages/{message_id}`: 获取单条消息详情。
    *   `PUT /api/v1/push/messages/{message_id}/read`: 标记消息为已读。
*   **消息接收Webhook (公开或特定Token验证):**
    *   `POST /webhooks/push/{source_identifier}`: 接收外部系统推送来的消息。
        *   `{source_identifier}`: 用于识别是哪个推送来源，如 `wechat_mp_1`, `dingtalk_bot_sales`。
        *   这个接口的安全性需要特别考虑，例如使用预共享密钥、IP白名单等。

### 4.5. 其他接口

*   **首页 (`/`)**:
    *   这个通常由前端路由处理，或者后端返回一个静态的 `index.html` 文件，其中包含备案信息等。
    *   如果后端直接返回，可以是一个简单的 FastAPI 路由:
        ```python
        from fastapi.responses import HTMLResponse

        @app.get("/", response_class=HTMLResponse)
        async def read_root():
            return """
            <html>
                <head><title>yend2</title></head>
                <body>
                    <h1>欢迎来到 yend2</h1>
                    <p>备案号：你的备案号</p>
                    <!-- 可以放一张图片 -->
                    <img src="/static/logo.png" alt="logo">
                </body>
            </html>
            """
        ```
*   **`/md` 接口 (建议更名为 `/api/v1/debug/echo` 或类似):**
    *   **路径:** `/api/v1/debug/echo`
    *   **方法:** `GET`, `POST` (支持 `application/x-www-form-urlencoded` 和 `application/json`)
    *   **功能:** 用于测试请求，返回请求的相关信息。
    *   **响应:**
        ```json
        {
            "code": 0,
            "message": "success",
            "data": {
                "received_params": {}, // GET query params or POST body
                "headers": {}, // 部分关键请求头
                "client_ip": "140.235.140.171",
                "request_method": "POST",
                "request_url": "http://pscly.cc/api/v1/debug/echo",
                "timestamp_utc": "2025-05-21T03:41:52Z", // 建议使用UTC时间
                "timestamp_local": "2025-05-21 11:41:52", // 带时区
                "server_time_epoch": 1747798912.7506425
            }
        }
        ```

## 5. 配置文件说明

使用 `.env` 文件进行配置是很好的实践。建议提供一个 `.env.example` 文件作为模板。

**.env.example (模板文件，不应包含真实密码):**
```ini
# 应用配置
APP_ENV=development # 可选: development, testing, production
DEBUG_MODE=True     # FastAPI的调试模式
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=your_very_secret_and_strong_key_please_change_me # 用于JWT签名等，务必修改且保密
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Token有效时间 (分钟)

# 数据库配置 (SQLAlchemy URL)
# 示例:
# PostgreSQL: postgresql+asyncpg://user:password@host:port/dbname
# MySQL: mysql+aiomysql://user:password@host:port/dbname
# SQLite (异步): sqlite+aiosqlite:///./yend2.db
# SQLite (同步, 不推荐用于FastAPI生产): sqlite:///./yend2.db
DATABASE_URL='postgresql+asyncpg://postgres:123456@192.168.11.110:5432/yend'

# 跨域配置 (CORS)
# 允许的源列表，用逗号分隔，例如: http://localhost:3000,https://yourdomain.com
CORS_ALLOWED_ORIGINS='*' # 在开发时可以是 '*'，生产环境务必指定明确的域名

# 推送服务配置 (示例)
# WECHAT_APP_ID=
# WECHAT_APP_SECRET=
# DINGTALK_ROBOT_TOKEN_DEFAULT=

# 邮件服务配置 (如果需要邮件推送/找回密码等)
# MAIL_SERVER=
# MAIL_PORT=
# MAIL_USERNAME=
# MAIL_PASSWORD=
# MAIL_USE_TLS=True
# MAIL_SENDER=

# (其他服务配置...)

```

## 6. 项目目录结构

这是一个推荐的单体仓库 (monorepo) 结构，将前后端代码放在同一个 Git 仓库中，但分别位于不同的子目录。

[文件结构](./readme2.md#结构)

## 7. 开发环境搭建与运行

### 7.1. 后端 (FastAPI)

克隆仓库: git clone 

进入后端目录: cd yend2/backend

创建虚拟环境: python -m venv venv

激活虚拟环境:

    Linux/macOS: source venv/bin/activate

    Windows: venv\Scripts\activate

安装依赖: pip install -r requirements.txt

配置环境变量: 复制 .env.example 为 .env，并修改其中的配置，特别是 DATABASE_URL 和 SECRET_KEY。

数据库迁移 (如果使用 Alembic):

    alembic revision -m "create_initial_tables" (如果首次创建)

    alembic upgrade head

运行开发服务器: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

    --reload 会在代码变动时自动重启服务器。

### 7.2. 前端 (Vue3 + UniApp)

进入前端目录: cd yend2/frontend (从项目根目录)

安装依赖: npm install (或 yarn install 或 pnpm install)

配置环境变量: 根据需要修改 .env.development (Vite/Vue CLI 会自动加载)。通常需要配置 VITE_API_BASE_URL=http://localhost:8000/api/v1。

运行开发服务器 (Web): npm run dev (或 yarn dev 或 pnpm dev)

- 编译到不同平台 (UniApp):
    - 微信小程序: npm run dev:mp-weixin
    - H5: npm run dev:h5
    - (其他平台请参考 UniApp 文档)

## 剩余问题

- [ ] 前端方面
    - [ ] 导航栏没有成功出现
    - [ ] 消息推送接口不完整
