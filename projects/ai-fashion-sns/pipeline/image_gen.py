"""Gemini/GrokのAPIで画像を生成する。プロンプトはClaude側で作成済みのものを受け取る。

モデル名はAPI提供元の更新頻度が高いため、実際に動かす際は最新のドキュメントで
モデルIDを確認・調整すること。
"""

import base64

import requests

import config

GEMINI_MODEL = "gemini-2.5-flash-image"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)

GROK_IMAGE_MODEL = "grok-2-image-1212"
GROK_URL = "https://api.x.ai/v1/images/generations"


def generate_with_gemini(prompt: str) -> bytes:
    """Gemini APIで試作画像を1枚生成する。"""
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY が未設定です")

    response = requests.post(
        GEMINI_URL,
        params={"key": config.GEMINI_API_KEY},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        },
        timeout=60,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Gemini画像生成に失敗しました: {response.status_code} {response.text}"
        )

    data = response.json()
    parts = data["candidates"][0]["content"]["parts"]
    for part in parts:
        inline_data = part.get("inlineData")
        if inline_data and inline_data.get("data"):
            return base64.b64decode(inline_data["data"])
    raise RuntimeError("Gemini応答に画像データが含まれていません")


def generate_with_grok(prompt: str, count: int) -> list[bytes]:
    """Grok APIで構図・ポーズ違いの画像をcount枚生成する。"""
    if not config.GROK_API_KEY:
        raise RuntimeError("GROK_API_KEY が未設定です")

    response = requests.post(
        GROK_URL,
        headers={"Authorization": f"Bearer {config.GROK_API_KEY}"},
        json={
            "model": GROK_IMAGE_MODEL,
            "prompt": prompt,
            "n": count,
            "response_format": "b64_json",
        },
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Grok画像生成に失敗しました: {response.status_code} {response.text}"
        )

    data = response.json()
    images = []
    for item in data.get("data", []):
        if item.get("b64_json"):
            images.append(base64.b64decode(item["b64_json"]))
        elif item.get("url"):
            img_response = requests.get(item["url"], timeout=60)
            img_response.raise_for_status()
            images.append(img_response.content)
    return images
