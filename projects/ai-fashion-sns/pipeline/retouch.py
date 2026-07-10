"""選ばれた上位5枚を補正・高品質化する（Meitu代替のAPIベース処理）。

Stability AIのFast Upscale APIを使い、画質向上を行う。
"""

import requests

import config

STABILITY_UPSCALE_URL = "https://api.stability.ai/v2beta/stable-image/upscale/fast"


def retouch(image_bytes: bytes) -> bytes:
    """Stability AIのFast Upscale APIで補正済みの画像を返す。"""
    if not config.STABILITY_API_KEY:
        raise RuntimeError("STABILITY_API_KEY が未設定です")

    response = requests.post(
        STABILITY_UPSCALE_URL,
        headers={
            "authorization": f"Bearer {config.STABILITY_API_KEY}",
            "accept": "image/*",
        },
        files={"image": ("image.png", image_bytes, "image/png")},
        timeout=60,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Stability AI upscale に失敗しました: {response.status_code} {response.text}"
        )
    return response.content
