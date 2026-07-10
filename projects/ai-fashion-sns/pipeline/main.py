"""パイプラインの実行部分のエントリーポイント。

トレンド取得・プロンプト生成・20枚の採点・上位5枚の選定・学習分析は
Claude自身が行うため、このスクリプトはその指示を受けて
「画像生成」「補正」「Driveアップロード」という外部API呼び出しのみを担当する。

想定される呼ばれ方:
    generated = [image_gen.generate_with_grok(prompt, n) for ...]
    top5 = <Claudeが採点して選んだ5枚>
    for image in top5:
        retouched = retouch.retouch(image)
        drive_upload.upload(retouched, filename)
"""

import image_gen
import retouch
import drive_upload
import state_store


def run_generation_step(prompt: str, images_per_day: int) -> list[bytes]:
    """プロンプトから画像を生成する（Gemini試作 + Grokでバリエーション量産）。"""
    draft = image_gen.generate_with_gemini(prompt)
    variations = image_gen.generate_with_grok(prompt, images_per_day - 1)
    return [draft] + variations


def run_finalize_step(selected_images: list[bytes], filenames: list[str]) -> list[str]:
    """選ばれた画像を補正し、Googleドライブへアップロードする。"""
    file_ids = []
    for image_bytes, filename in zip(selected_images, filenames):
        retouched = retouch.retouch(image_bytes)
        file_id = drive_upload.upload(retouched, filename)
        file_ids.append(file_id)
    return file_ids


if __name__ == "__main__":
    raise SystemExit(
        "このスクリプトは単体では実行できません。"
        "Claudeがトレンド取得・プロンプト生成・採点を行った上で、"
        "run_generation_step / run_finalize_step を呼び出す想定です。"
    )
