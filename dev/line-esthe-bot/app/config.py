import os
from functools import lru_cache


class Settings:
    line_channel_access_token: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    line_channel_secret: str = os.getenv("LINE_CHANNEL_SECRET", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # Gemini free tier is used for MVP summarization instead of OpenAI (cost).
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", str(6 * 60 * 60)))
    scraper_timeout_seconds: int = int(os.getenv("SCRAPER_TIMEOUT_SECONDS", "8"))
    max_concurrent_scrapes: int = int(os.getenv("MAX_CONCURRENT_SCRAPES", "3"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
