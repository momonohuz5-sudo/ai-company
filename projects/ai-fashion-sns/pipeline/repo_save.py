"""補正済みの画像をリポジトリ内のoutputフォルダに保存する(git commit/pushは呼び出し側で行う)。"""

import os
from datetime import date

import config


def save(image_bytes: bytes, filename: str, day: date | None = None) -> str:
    """画像を output/YYYY-MM-DD/filename として保存し、保存先パスを返す。"""
    day = day or date.today()
    day_dir = os.path.join(config.OUTPUT_DIR, day.isoformat())
    os.makedirs(day_dir, exist_ok=True)
    path = os.path.join(day_dir, filename)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return path
