"""選ばれた上位5枚を補正・高品質化する（Meitu代替のAPIベース処理）。"""

import config


def retouch(image_bytes: bytes) -> bytes:
    """画像補正APIを呼び出し、補正済みの画像を返す。"""
    if not config.RETOUCH_API_KEY:
        raise RuntimeError("RETOUCH_API_KEY が未設定です")
    # TODO: 補正API（Stability AI / Photoroom等、未選定）を呼び出す実装
    raise NotImplementedError
