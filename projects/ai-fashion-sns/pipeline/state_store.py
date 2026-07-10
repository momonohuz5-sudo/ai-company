"""日次の実行ログを保存・読み込みする（学習ループの土台）。"""

import json
import os
from datetime import date

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")


def save_daily_log(day: date, data: dict) -> str:
    """当日の実行結果（プロンプト・生成情報・採点・選定結果等）を保存する。"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    path = os.path.join(LOGS_DIR, f"{day.isoformat()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def load_daily_log(day: date) -> dict | None:
    """指定日のログを読み込む。存在しなければNoneを返す。"""
    path = os.path.join(LOGS_DIR, f"{day.isoformat()}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)
