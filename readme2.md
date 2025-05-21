# 文件结构

## toc

1. [文件结构](#文件结构)
    1. [toc](#toc)
    2. [结构](#结构)
    3. [命名约定说明:](#命名约定说明)

## 结构

yend2/
├── backend/                       # 后端 FastAPI 项目
│   ├── app/                       # 应用核心代码 (或者直接叫 yend2_api)
│   │   ├── api/                   # API 路由模块
│   │   │   ├── v1/                # API 版本 v1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/     # 各模块的路由处理函数
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py      # 认证相关接口
│   │   │   │   │   ├── users.py     # 用户管理接口
│   │   │   │   │   ├── navigation.py# 导航页接口
│   │   │   │   │   └── push.py      # 推送相关接口
│   │   │   │   └── deps.py        # FastAPI 依赖项 (如获取当前用户)
│   │   │   └── router.py          # 组装 v1 版本的总路由
│   │   ├── core/                  # 核心配置、安全等
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Pydantic 配置加载
│   │   │   └── security.py        # 密码哈希、JWT生成与校验
│   │   ├── crud/                  # 数据库操作 (Create, Read, Update, Delete)
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # CRUD 基类 (可选)
│   │   │   ├── crud_user.py
│   │   │   ├── crud_navigation.py
│   │   │   └── crud_push.py
│   │   ├── db/                    # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── base_class.py      # SQLAlchemy Base (声明式基类)
│   │   │   ├── session.py         #数据库会话管理 (engine, SessionLocal)
│   │   │   └── init_db.py         # 初始化数据库及超级用户 (可选)
│   │   ├── models/                # SQLAlchemy 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── navigation.py
│   │   │   └── push.py
│   │   ├── schemas/               # Pydantic 数据校验模型 (API输入输出)
│   │   │   ├── __init__.py
│   │   │   ├── token.py
│   │   │   ├── user.py
│   │   │   ├── navigation.py
│   │   │   └── push.py
│   │   ├── services/              # 业务逻辑服务 (可选，如果逻辑复杂)
│   │   │   └── ...
│   │   ├── static/                # 静态文件 (如首页引用的logo)
│   │   │   └── logo.png
│   │   └── main.py                # FastAPI 应用实例和启动入口
│   ├── alembic/                   # Alembic 数据库迁移文件夹 (运行 `alembic init alembic`)
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── alembic.ini                # Alembic 配置文件
│   ├── tests/                     # 测试代码
│   │   ├── __init__.py
│   │   ├── conftest.py            # Pytest 配置文件
│   │   └── api/
│   │       └── v1/
│   │           └── test_auth.py
│   ├── .env                       # 环境变量 (不提交到git)
│   ├── .env.example               # 环境变量模板
│   ├── .gitignore
│   ├── prestart.sh                # (可选) 启动前执行的脚本，如运行数据库迁移
│   └── requirements.txt           # Python 依赖
│
├── frontend/                      # 前端 Vue3 + UniApp 项目
│   ├── public/                    # 静态资源 (会被直接复制)
│   │   └── favicon.ico
│   ├── src/
│   │   ├── assets/                # 模块资源 (会被 webpack/vite 处理)
│   │   ├── components/            # 可复用组件
│   │   │   └── MyComponent.vue
│   │   ├── views/ or pages/       # 页面组件
│   │   │   ├── HomeView.vue
│   │   │   └── LoginView.vue
│   │   ├── router/                # Vue Router 配置
│   │   │   └── index.js
│   │   ├── store/                 # Pinia 状态管理
│   │   │   └── index.js
│   │   ├── api/                   # 前端调用后端API的封装
│   │   │   ├── index.js           # Axios 实例和拦截器
│   │   │   └── modules/
│   │   │       ├── auth.js
│   │   │       └── navigation.js
│   │   ├── utils/                 # 工具函数
│   │   ├── App.vue                # 根组件
│   │   └── main.js                # 应用入口 (Vue实例化)
│   ├── .env.development           # 开发环境变量 (Vite/Vue CLI)
│   ├── .env.production            # 生产环境变量 (Vite/Vue CLI)
│   ├── .gitignore
│   ├── package.json
│   ├── vite.config.js or vue.config.js # Vite 或 Vue CLI 配置文件
│   └── postcss.config.js          # (如果使用 PostCSS)
│
├── .dockerignore                  # Docker 构建时忽略的文件
├── docker-compose.yml             # (可选) Docker Compose 配置，用于本地开发和部署
├── LICENSE                        # 项目许可证 (如 MIT)
└── README.md                      # 你正在阅读的这个文件

## 命名约定说明:

Python 包/目录名: snake_case (全小写，下划线分隔)，例如 api, core, db, push_services。

Python 文件名: snake_case.py, 例如 main.py, config.py, crud_user.py。

Python 类名: PascalCase (首字母大写驼峰)，例如 User, NavigationGroup, PushMessage。

Python 函数/方法/变量名: snake_case, 例如 get_current_user, db_session, item_id。

FastAPI 路径操作函数名: 推荐与功能相关，例如 read_users_me, create_item_for_group。

API 端点路径: kebab-case (短横线分隔)，例如 /api/v1/navigation-groups/{group_id}/items。

数据库表名: snake_case (全小写，下划线分隔)，通常是模型类名的小写复数形式，例如 users, navigation_groups, push_messages。

数据库列名: snake_case，例如 user_id, created_at, is_active。

Vue/UniApp 组件文件名: PascalCase.vue (首字母大写驼峰)，例如 UserProfile.vue, NavItem.vue。

JavaScript/TypeScript 文件名 (非组件): camelCase.js 或 kebab-case.js 都可以，保持一致性。例如 apiService.js 或 api-service.js。

JavaScript/TypeScript 变量/函数名: camelCase，例如 fetchUserData, currentUser。
