"""パイプラインの実行部分のエントリーポイント。

トレンド取得・プロンプト生成・20枚の採点・上位5枚の選定・学習分析は
Claude自身が行うため、このスクリプトはその指示を受けて
「画像生成」「補正」「リポジトリへの保存」という外部API呼び出し・
ファイル操作のみを担当する。保存後のgit commit/pushは呼び出し側(Claude)が行う。

想定される呼ばれ方:
    generated = run_generation_step(prompt, config.IMAGES_PER_DAY)
    top5 = <Claudeが採点して選んだ5枚>
    paths = run_finalize_step(top5, filenames)
"""

import image_gen
import retouch
import repo_save
import state_store


def run_generation_step(prompt: str, images_per_day: int) -> list[bytes]:
    """プロンプトから画像を生成する（Gemini試作 + Grokでバリエーション量産）。"""
    draft = image_gen.generate_with_gemini(prompt)
    variations = image_gen.generate_with_grok(prompt, images_per_day - 1)
    return [draft] + variations


def run_finalize_step(selected_images: list[bytes], filenames: list[str]) -> list[str]:
    """選ばれた画像を補正し、リポジトリのoutputフォルダに保存する。"""
    saved_paths = []
    for image_bytes, filename in zip(selected_images, filenames):
        retouched = retouch.retouch(image_bytes)
        path = repo_save.save(retouched, filename)
        saved_paths.append(path)
    return saved_paths


if __name__ == "__main__":
    raise SystemExit(
        "このスクリプトは単体では実行できません。"
        "Claudeがトレンド取得・プロンプト生成・採点を行った上で、"
        "run_generation_step / run_finalize_step を呼び出す想定です。"
    )
