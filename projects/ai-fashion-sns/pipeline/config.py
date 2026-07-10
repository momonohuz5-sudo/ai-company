import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
RETOUCH_API_KEY = os.environ.get("RETOUCH_API_KEY", "")

# 保存先: 当面はGoogleドライブ等の外部サービスではなく、このリポジトリ内に
# 画像を保存してgit pushする方式にする(認証設定が不要ですぐ動かせるため)。
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# 1日に生成する画像枚数と、最終的に残す枚数
IMAGES_PER_DAY = 20
TOP_N = 5
