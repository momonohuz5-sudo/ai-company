import os
from dotenv import load_dotenv

load_dotenv()

# ==============================
# エリア定義
# ==============================
AREAS = {
    "azabu": {
        "name": "麻布",
        "calendar_id": os.getenv("CALENDAR_ID_AZABU", ""),
        "esthe_page_url": os.getenv("ESTHE_URL_AZABU", ""),
        "linked_areas": [],
        "enabled": True,
    },
    "kanda": {
        "name": "神田",
        "calendar_id": os.getenv("CALENDAR_ID_KANDA", ""),
        "esthe_page_url": os.getenv("ESTHE_URL_KANDA", ""),
        "linked_areas": ["nihonbashi"],  # 日本橋と同時クリック
        "enabled": True,
    },
    "nihonbashi": {
        "name": "日本橋",
        "calendar_id": os.getenv("CALENDAR_ID_NIHONBASHI", ""),
        "esthe_page_url": os.getenv("ESTHE_URL_NIHONBASHI", ""),
        "linked_areas": ["kanda"],  # 神田と同時クリック
        "enabled": True,
    },
    "omori": {
        "name": "大森",
        "calendar_id": os.getenv("CALENDAR_ID_OMORI", ""),
        "esthe_page_url": os.getenv("ESTHE_URL_OMORI", ""),
        "linked_areas": [],
        "enabled": True,
    },
    "tamachi": {
        "name": "田町",
        "calendar_id": os.getenv("CALENDAR_ID_TAMACHI", ""),
        "esthe_page_url": os.getenv("ESTHE_URL_TAMACHI", ""),
        "linked_areas": [],
        "enabled": True,
    },
    "hatchobori": {
        "name": "八丁堀",
        "calendar_id": os.getenv("CALENDAR_ID_HATCHOBORI", ""),
        "esthe_page_url": os.getenv("ESTHE_URL_HATCHOBORI", ""),
        "linked_areas": [],
        "enabled": False,  # 追加予定のため初期は無効
    },
}

# ==============================
# エステ魂 認証・URL
# ==============================
ESTHE_LOGIN_URL = os.getenv("ESTHE_LOGIN_URL", "")
ESTHE_ID = os.getenv("ESTHE_ID", "")
ESTHE_PASSWORD = os.getenv("ESTHE_PASSWORD", "")
ESTHE_URL_APPEAL = os.getenv("ESTHE_URL_APPEAL", "")    # 集客ワンクリックアピール
ESTHE_URL_REALTIME = os.getenv("ESTHE_URL_REALTIME", "")  # リアルタイム集客

# ==============================
# 営業時間 (10:00 〜 翌5:30)
# ==============================
BUSINESS_START_HOUR = 10
BUSINESS_START_MINUTE = 0
BUSINESS_END_HOUR = 5    # 翌日
BUSINESS_END_MINUTE = 30

# ==============================
# ポチルール
# ==============================
MAX_CLICKS_PER_DAY = 10
MIN_INTERVAL_MINUTES = 100  # 1時間40分

# 禁止時間帯: XX:55 〜 XX:10
PROHIBITED_START_MINUTE = 55
PROHIBITED_END_MINUTE = 10
# 禁止帯に当たる場合は XX:53 に押す
PROHIBITED_FALLBACK_MINUTE = 53

# XX:30 → XX:23 に押す
THIRTY_MINUTE_OVERRIDE_TARGET = 30
THIRTY_MINUTE_OVERRIDE_FALLBACK = 23

# 退出15分前がベストタイミング
BEST_BEFORE_EXIT_MINUTES = 15

# ==============================
# システム設定
# ==============================
CALENDAR_REFRESH_MINUTES = 5    # カレンダー取得間隔
WEB_PORT = 5000                 # 監視画面のポート
TIMEZONE = "Asia/Tokyo"
STATE_FILE = "data/state.json"
LOG_FILE = "data/auto_pochi.log"
