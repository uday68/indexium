import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _HAVE_SETTINGS = True
except ImportError:
    from pydantic import BaseModel as BaseSettings
    _HAVE_SETTINGS = False


class Settings(BaseSettings):
    PROJECT_NAME: str = "Indexium"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Host & Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Default Ranking Algorithm: "bm25", "tfidf", "pagerank"
    DEFAULT_RANKER: str = "bm25"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./indexium.db")

    # Redis Cache
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    CACHE_TTL_SECONDS: int = 300

    # Crawler Settings
    CRAWLER_MAX_DEPTH: int = 2
    CRAWLER_MAX_PAGES: int = 50
    CRAWLER_POLITENESS_DELAY: float = 0.2
    CRAWLER_USER_AGENT: str = "IndexiumCrawler/1.0"

    # Storage Paths
    INDEX_STORAGE_PATH: str = "./index_data/inverted_index.json"

    if _HAVE_SETTINGS:
        model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
