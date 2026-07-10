"""選ばれた上位5枚を補正・高品質化する（Meitu代替のAPIベース処理）。

Stability AIのFast Upscale APIを使い、画質向上を行う。
"""

import requests

import config

STABILITY_UPSCALE_URL = "https://api.stability.ai/v2beta/stable-image/upscale/fast"


def retouch(image_bytes: bytes) -> bytes:
    """Stability AIのFast Upscale APIで補正済みの画像を返す。

    STABILITY_API_KEYが未設定の場合は補正をスキップし、元画像をそのまま返す
    (補正は必須のステップではないため)。
    """
    if not config.STABILITY_API_KEY:
        return image_bytes

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
