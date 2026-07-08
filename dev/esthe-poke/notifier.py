"""ポチ実行時のLINE通知。

注意: LINE Notifyは2025年3月末でサービス終了しているため、
LINE公式アカウントのMessaging API(プッシュメッセージ)を使う。
必要な環境変数:
  - LINE_CHANNEL_ACCESS_TOKEN: Messaging APIのチャネルアクセストークン
  - LINE_TARGET_ID: 通知を送る先のユーザーID or グループID
"""

from __future__ import annotations

import os

import requests

from config import LINE_CHANNEL_ACCESS_TOKEN_ENV, LINE_TARGET_ID_ENV

_PUSH_URL = "https://api.line.me/v2/bot/message/push"


def notify_poke(unit_label: str, sites: tuple[str, ...], reason: str) -> None:
    token = os.environ[LINE_CHANNEL_ACCESS_TOKEN_ENV]
    target_id = os.environ[LINE_TARGET_ID_ENV]

    text = f"ポチします\nエリア: {unit_label}\n対象: {', '.join(sites)}\n理由: {reason}"

    resp = requests.post(
        _PUSH_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"to": target_id, "messages": [{"type": "text", "text": text}]},
        timeout=10,
    )
    resp.raise_for_status()
