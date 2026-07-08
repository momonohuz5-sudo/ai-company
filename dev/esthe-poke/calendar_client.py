"""Googleカレンダーから空き状況を取得するモジュール。

TODO: サービスアカウントの認証情報とカレンダーIDが未確定のため、
実運用には以下が必要:
  - GOOGLE_SERVICE_ACCOUNT_FILE 環境変数(サービスアカウントのJSON鍵パス)
  - 各カレンダーを、そのサービスアカウントに共有設定しておくこと
  - config.py の calendar_ids_env に対応する環境変数へ実際のカレンダーIDを設定

現状は依存パッケージ(google-api-python-client, google-auth)は未導入。
`pip install google-api-python-client google-auth` の追加が必要。
"""

from __future__ import annotations

import os
from datetime import datetime

from rules import Event

_SERVICE_ACCOUNT_FILE_ENV = "GOOGLE_SERVICE_ACCOUNT_FILE"


def _get_calendar_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    key_path = os.environ[_SERVICE_ACCOUNT_FILE_ENV]
    creds = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )
    return build("calendar", "v3", credentials=creds)


def fetch_events(calendar_id: str, window_start: datetime, window_end: datetime) -> tuple[Event, ...]:
    """指定カレンダーの、window_start〜window_end に重なる予定を取得する。"""
    service = _get_calendar_service()
    resp = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=window_start.isoformat(),
            timeMax=window_end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = []
    for item in resp.get("items", []):
        start = item["start"].get("dateTime")
        end = item["end"].get("dateTime")
        if start is None or end is None:
            continue  # 終日予定はスキップ(施術予約は時刻指定される想定)
        events.append(Event(start=datetime.fromisoformat(start), end=datetime.fromisoformat(end)))
    return tuple(events)


def fetch_merged_events(
    calendar_ids: tuple[str, ...], window_start: datetime, window_end: datetime
) -> tuple[Event, ...]:
    """複数カレンダーの予定をまとめて返す(神田+日本橋のような合算ユニット用)。"""
    merged: list[Event] = []
    for calendar_id in calendar_ids:
        merged.extend(fetch_events(calendar_id, window_start, window_end))
    return tuple(merged)
