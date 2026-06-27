"""
エステ魂 自動ポチシステム 起動スクリプト

起動前に:
  1. cp .env.example .env  して認証情報・URLを記入
  2. credentials/credentials.json を配置（Google Calendar API）
  3. pip install -r requirements.txt
  4. playwright install chromium

起動:
  python run.py
"""
import asyncio
import logging
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

from src.config import LOG_FILE, WEB_PORT
from src.scheduler import AutoPochiScheduler

os.makedirs("data", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

if __name__ == "__main__":
    # 監視用Webサーバーを起動（スマホからアクセス可能）
    from web.app import start as start_web
    start_web()
    logging.getLogger(__name__).info(f"監視画面: http://localhost:{WEB_PORT}")

    # メインスケジューラー起動
    scheduler = AutoPochiScheduler()
    asyncio.run(scheduler.start())
