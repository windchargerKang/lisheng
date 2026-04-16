"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    PROJECT_NAME: str = "渠道销售管理系统"
    API_V1_PREFIX: str = "/api/v1"

    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./channel_sales.db"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时

    class Config:
        env_file = ".env"


settings = Settings()
