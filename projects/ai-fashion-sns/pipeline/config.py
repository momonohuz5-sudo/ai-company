import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
RETOUCH_API_KEY = os.environ.get("RETOUCH_API_KEY", "")

# サービスアカウントのJSON認証情報そのもの（ファイルパスではなく中身の文字列）。
# 実行環境ごとにコンテナが作り直されるため、ファイルパスではなく環境変数で渡す。
GOOGLE_DRIVE_CREDENTIALS_JSON = os.environ.get("GOOGLE_DRIVE_CREDENTIALS_JSON", "")

# Googleドライブの保存先フォルダID
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "")

# 1日に生成する画像枚数と、最終的に残す枚数
IMAGES_PER_DAY = 20
TOP_N = 5
