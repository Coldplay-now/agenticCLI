"""
配置管理模块
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    """应用配置"""
    
    # 应用信息
    app_name: str = "{{project_name}}"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 数据库配置
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./{{project_name}}.db")
    
    # API 配置
    api_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list = ["*"]


settings = Settings()

