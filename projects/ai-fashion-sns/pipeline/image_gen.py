"""Gemini/GrokのAPIで画像を生成する。プロンプトはClaude側で作成済みのものを受け取る。"""

import config


def generate_with_gemini(prompt: str) -> bytes:
    """Gemini APIで試作画像を1枚生成する。"""
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY が未設定です")
    # TODO: Gemini画像生成APIを呼び出す実装
    raise NotImplementedError


def generate_with_grok(prompt: str, count: int) -> list[bytes]:
    """Grok APIで構図・ポーズ違いの画像をcount枚生成する。"""
    if not config.GROK_API_KEY:
        raise RuntimeError("GROK_API_KEY が未設定です")
    # TODO: Grok画像生成APIを呼び出す実装
    raise NotImplementedError
