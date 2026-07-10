# AIポートレート・アート作品集パイプライン（MVP）

`projects/ai-fashion-sns/ARCHITECTURE.md` の設計に基づく実装。
アートスタイル決定・プロンプト生成・採点・学習分析はClaude自身が担当するため、
このディレクトリには外部APIを叩く部分（画像生成・補正）と保存処理のみを置く。

## セットアップ

1. 依存パッケージをインストール
   ```
   pip install -r requirements.txt
   ```
2. 本番（毎朝のRoutine）では、この環境の「環境変数」設定に下表の変数を登録する
   （`.env` はローカルで手元検証したい場合のみ使用。コミットしない）
3. 保存先は当面Googleドライブ等の外部サービスではなく、`output/YYYY-MM-DD/` に
   保存してそのままgit commit & pushする方式（認証設定が不要ですぐ動かせる）

## 必要なAPIキー（環境変数として登録）

| 変数名 | 用途 |
|---|---|
| `GEMINI_API_KEY` | Gemini画像生成 |
| `GROK_API_KEY` | Grok画像生成（構図・ポーズのバリエーション） |
| `STABILITY_API_KEY` | 画像補正API（Stability AI、Fast Upscaleで高品質化） |

## 実行

```
python main.py
```

Claude Code の Routine（毎朝の定期トリガー）から呼び出す想定。
アートスタイル決定・プロンプト生成・採点・学習分析はこのスクリプトの外側（Claude自身の推論）で行い、
本スクリプトは「生成済みプロンプトを受け取って画像を作る」「選ばれた5枚を補正してoutput/に保存する」
という実行部分のみを担当する。保存後のgit commit/pushはRoutine側(Claude)が行う。

## 現状

`image_gen.py` / `retouch.py` / `repo_save.py` はすべて実装済み。
GEMINI_API_KEY・GROK_API_KEYは環境変数に登録済み。STABILITY_API_KEYの取得待ち。
モデル名（`GEMINI_MODEL` / `GROK_IMAGE_MODEL`）は各API提供元の更新頻度が高いため、
初回実行時にエラーが出た場合は最新のドキュメントで確認・調整すること。

## 将来的な移行

保存先をGoogleドライブ等に切り替えたくなった場合は、`repo_save.py` と同じ
インターフェース（`save(image_bytes, filename) -> str`）を持つモジュールに
差し替えるだけでよい設計にしている。
