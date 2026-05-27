"""設定管理モジュール"""

import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    """アプリケーション設定"""

    # Claude API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # note設定
    NOTE_EMAIL = os.getenv("NOTE_EMAIL", "")
    NOTE_PASSWORD = os.getenv("NOTE_PASSWORD", "")
    NOTE_USER_URLNAME = os.getenv("NOTE_USER_URLNAME", "")
    NOTE_MAGAZINE_ID = os.getenv("NOTE_MAGAZINE_ID", "")
    NOTE_ARTICLE_PRICE = int(os.getenv("NOTE_ARTICLE_PRICE", "500"))

    # スケジューリング
    PUBLISH_TIME = os.getenv("PUBLISH_TIME", "09:00")
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Tokyo")

    # PokerNews
    POKERNEWS_SCRAPE_ENABLED = os.getenv("POKERNEWS_SCRAPE_ENABLED", "true").lower() == "true"
    POKERNEWS_API_KEY = os.getenv("POKERNEWS_API_KEY", "")

    # ログ
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # パス
    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    LOGS_DIR = PROJECT_ROOT / "logs"
    PROMPTS_DIR = DATA_DIR / "prompts"
    ARTICLES_DIR = OUTPUT_DIR / "articles"
    IMAGES_DIR = OUTPUT_DIR / "images"
    BACKUP_DIR = OUTPUT_DIR / "backup"
    DB_PATH = PROJECT_ROOT / "database.db"

    @classmethod
    def validate(cls):
        """必須設定のバリデーション"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")

        # ディレクトリ作成
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.ARTICLES_DIR.mkdir(exist_ok=True)
        cls.IMAGES_DIR.mkdir(exist_ok=True)
        cls.BACKUP_DIR.mkdir(exist_ok=True)
