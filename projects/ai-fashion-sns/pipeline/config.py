import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
RETOUCH_API_KEY = os.environ.get("RETOUCH_API_KEY", "")

# OAuth(デスクトップアプリ)方式の認証情報。組織ポリシーでサービスアカウント
# の鍵ファイル発行がブロックされているため、自分のGoogleアカウントに対する
# リフレッシュトークン方式を採用する。
GOOGLE_DRIVE_CLIENT_ID = os.environ.get("GOOGLE_DRIVE_CLIENT_ID", "")
GOOGLE_DRIVE_CLIENT_SECRET = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET", "")
GOOGLE_DRIVE_REFRESH_TOKEN = os.environ.get("GOOGLE_DRIVE_REFRESH_TOKEN", "")

# Googleドライブの保存先フォルダID
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "")

# 1日に生成する画像枚数と、最終的に残す枚数
IMAGES_PER_DAY = 20
TOP_N = 5
