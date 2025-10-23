"""
应用配置管理
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置类"""

    # OpenAI配置 - 使用PBL专用环境变量名避免冲突
    openai_api_key: str = Field(alias="PBL_AI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="PBL_AI_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="PBL_AI_BASE_URL")

    # 模型参数配置
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4000

    # 支持不同Agent使用不同模型（可选）
    agent1_model: Optional[str] = None  # 如果不指定，使用openai_model
    agent2_model: Optional[str] = None
    agent3_model: Optional[str] = None

    # 服务器配置
    host: str = "localhost"
    port: int = 48097
    debug: bool = True

    # 数据库配置
    database_url: str = "sqlite:///./app.db"

    # CORS配置
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:48098",
        "http://1.95.87.0:48098",
    ]

    # 性能配置
    max_timeout: int = 90  # 最大响应时间（秒）
    agent1_timeout: int = 20  # Agent1超时时间
    agent2_timeout: int = 25  # Agent2超时时间
    agent3_timeout: int = 40  # Agent3超时时间

    # 系统行为配置
    use_chinese_response: bool = True  # 默认使用中文回答

    class Config:
        env_file = ".env"


# 全局设置实例
settings = Settings()