# AIファッション自動投稿パイプライン（MVP）

`projects/ai-fashion-sns/ARCHITECTURE.md` の設計に基づく実装。
トレンド取得・プロンプト生成・採点・学習分析はClaude自身が担当するため、
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
| `RETOUCH_API_KEY` | 画像補正API（Stability AI / Photoroom等、未選定） |

## 実行

```
python main.py
```

Claude Code の Routine（毎朝の定期トリガー）から呼び出す想定。
トレンド取得・プロンプト生成・採点・学習分析はこのスクリプトの外側（Claude自身の推論）で行い、
本スクリプトは「生成済みプロンプトを受け取って画像を作る」「選ばれた5枚を補正してoutput/に保存する」
という実行部分のみを担当する。保存後のgit commit/pushはRoutine側(Claude)が行う。

## 現状

まだ画像生成・補正のAPI呼び出しは未実装（雛形のみ）。
実際のAPIキーが揃った段階で `image_gen.py` / `retouch.py` の
TODO部分を実装する。`repo_save.py` は実装済み。

## 将来的な移行

保存先をGoogleドライブ等に切り替えたくなった場合は、`repo_save.py` と同じ
インターフェース（`save(image_bytes, filename) -> str`）を持つモジュールに
差し替えるだけでよい設計にしている。
