"""應用設定,從環境變數讀取。使用 pydantic-settings 自動驗證型別。"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "zhouyi"

    # External services
    n8n_ai_webhook: str = ""
    geo_api_url: str = "http://ip-api.com/json/"

    # CORS — 逗號分隔字串,讀取後切成 list
    cors_origins: str = "*"

    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """單例 settings,整個應用共用。"""
    return Settings()
