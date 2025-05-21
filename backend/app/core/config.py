# backend/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, EmailStr, field_validator, AnyHttpUrl
from typing import Optional, Any, List, Union, Dict # Union和Dict是为了更复杂的类型

class Settings(BaseSettings):
    """
    应用配置模型，从 .env 文件加载。
    """

    # --- 应用基础配置 ---
    PROJECT_NAME: str = "Yend2 Project"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1" # API 路由前缀
    APP_ENV: str = "development"  # 可选: development, testing, production
    DEBUG_MODE: bool = True      # FastAPI 的调试模式
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # --- 安全与认证 ---
    SECRET_KEY: str # 用于JWT签名等，务必在 .env 中设置一个强大且唯一的密钥
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # Token有效时间 (分钟)
    # ALGORITHM: str = "HS256" # JWT 签名算法，如果固定可以放在这里，或者在 security.py 中定义

    # --- 数据库配置 ---
    # 示例: postgresql+asyncpg://user:password@host:port/dbname
    DATABASE_URL: PostgresDsn # 使用 Pydantic 的 DSN 类型进行验证
    # Alembic 或其他同步操作可能需要一个同步的数据库 URL
    SYNC_DATABASE_URL: Optional[str] = None # 如果与 DATABASE_URL 不同，则需要设置

    # --- 跨域配置 (CORS) ---
    # 允许的源列表，用逗号分隔，例如: http://localhost:3000,https://yourdomain.com
    # 或者直接使用 '*' (不推荐用于生产环境)
    CORS_ALLOWED_ORIGINS: Union[List[str], str] = "*"

    # --- 推送服务配置 (示例，根据实际需要添加) ---
    # WECHAT_APP_ID: Optional[str] = None
    # WECHAT_APP_SECRET: Optional[str] = None
    # DINGTALK_ROBOT_TOKEN_DEFAULT: Optional[str] = None

    # --- 邮件服务配置 (如果需要邮件推送/找回密码等) ---
    # MAIL_SERVER: Optional[str] = None
    # MAIL_PORT: Optional[int] = None
    # MAIL_USERNAME: Optional[str] = None
    # MAIL_PASSWORD: Optional[str] = None # 存储敏感信息需谨慎
    # MAIL_USE_TLS: bool = True
    # MAIL_USE_SSL: bool = False
    # MAIL_SENDER: Optional[EmailStr] = None
    # MAIL_SENDER_NAME: Optional[str] = None

    # --- 其他自定义配置 ---
    # FIRST_SUPERUSER_USERNAME: EmailStr = "admin@example.com" # 初始超级用户的邮箱
    # FIRST_SUPERUSER_PASSWORD: str = "changethis" # 初始超级用户的密码

    # --- Pydantic Settings 配置 ---
    model_config = SettingsConfigDict(
        env_file=".env",             # 指定 .env 文件名
        env_file_encoding='utf-8',   # .env 文件编码
        case_sensitive=True,         # 环境变量名是否区分大小写
        extra='ignore'               # 'ignore': 忽略 .env 中多余的变量
                                     # 'forbid': 如果 .env 中有未在 Settings 中定义的变量则报错 (更严格)
    )

    # --- 字段验证器与转换器 ---
    @field_validator("SYNC_DATABASE_URL", mode="before")
    @classmethod
    def assemble_sync_database_url(cls, v: Optional[str], info) -> Any:
        """
        如果 SYNC_DATABASE_URL 未在 .env 中明确设置，
        则尝试从 DATABASE_URL (通常是异步的) 生成一个同步版本。
        """
        if isinstance(v, str) and v: # 如果已经提供了 SYNC_DATABASE_URL，则直接使用
            return v

        # info.data 是一个包含已解析字段的字典
        database_url_value = info.data.get("DATABASE_URL")
        if database_url_value:
            db_url_str = str(database_url_value) # PostgresDsn 转为字符串
            # 尝试将常见的异步驱动标识符替换为同步的或移除
            # 这部分逻辑可能需要根据你实际使用的数据库和驱动进行调整
            # 示例：将 +asyncpg (PostgreSQL) 或 +aiomysql (MySQL) 移除
            sync_url = db_url_str
            if "+asyncpg" in sync_url:
                sync_url = sync_url.replace("+asyncpg", "")
            elif "+aiomysql" in sync_url:
                sync_url = sync_url.replace("+aiomysql", "")
            elif "+aiosqlite" in sync_url: # SQLite 异步
                sync_url = sync_url.replace("+aiosqlite", "")

            # 对于 SQLite，异步通常是 'sqlite+aiosqlite:///./file.db'
            # 同步是 'sqlite:///./file.db'
            # 对于 PostgreSQL/MySQL，通常是移除异步驱动部分
            # 例如 'postgresql+asyncpg://' -> 'postgresql://'

            return sync_url
        # 如果 DATABASE_URL 也没有，则 SYNC_DATABASE_URL 保持 None 或可以抛出错误
        # raise ValueError("DATABASE_URL is not set, cannot assemble SYNC_DATABASE_URL")
        return None # 或者保持 None，让使用者处理

    @field_validator('CORS_ALLOWED_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Union[List[str], str]:
        """
        将 .env 中逗号分隔的 CORS 源字符串转换为列表。
        如果值是 '*'，则保持为字符串 '*'。
        """
        if isinstance(v, list): # 如果已经是列表 (例如在测试中直接设置)
            return v
        if isinstance(v, str):
            if v.strip() == '*':
                return "*" # 特殊处理 '*'
            # 按逗号分割，去除空白，并过滤掉空字符串
            origins = [origin.strip() for origin in v.split(',') if origin.strip()]
            # 可以进一步验证每个 origin 是否是有效的 URL
            # for origin in origins:
            #     try:
            #         AnyHttpUrl(origin) # Pydantic 的 URL 类型会进行验证
            #     except ValueError:
            #         raise ValueError(f"Invalid CORS origin: {origin}")
            return origins
        # 如果是其他类型或 None，可以返回默认值或抛出错误
        return [] # 默认返回空列表

# 创建一个全局可用的 settings 实例
settings = Settings()

# 你可以在这里添加一些启动时的检查，例如确保关键配置已设置
# if not settings.SECRET_KEY:
#     raise ValueError("SECRET_KEY is not set in the environment variables or .env file!")
# if settings.APP_ENV == "production" and settings.DEBUG_MODE:
#     import warnings
#     warnings.warn("DEBUG_MODE is True in a production environment. This is insecure.", UserWarning)