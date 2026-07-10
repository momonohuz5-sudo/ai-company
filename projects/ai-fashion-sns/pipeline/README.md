# AIファッション自動投稿パイプライン（MVP）

`projects/ai-fashion-sns/ARCHITECTURE.md` の設計に基づく実装。
トレンド取得・プロンプト生成・採点・学習分析はClaude自身が担当するため、
このディレクトリには外部APIを叩く部分（画像生成・補正・Driveアップロード）のみを置く。

## セットアップ

1. 依存パッケージをインストール
   ```
   pip install -r requirements.txt
   ```
2. 本番（毎朝のRoutine）では、この環境の「環境変数」設定に下表の変数を登録する
   （`.env` はローカルで手元検証したい場合のみ使用。コミットしない）
3. Google Driveの認証は、組織ポリシーでサービスアカウントの鍵ファイル発行がブロックされているため、
   OAuth(デスクトップアプリ)方式＋リフレッシュトークンを採用する
   （OAuth Playground等で一度だけ認可し、リフレッシュトークンを取得する）

## 必要なAPIキー・認証情報（環境変数として登録）

| 変数名 | 用途 |
|---|---|
| `GEMINI_API_KEY` | Gemini画像生成 |
| `GROK_API_KEY` | Grok画像生成（構図・ポーズのバリエーション） |
| `RETOUCH_API_KEY` | 画像補正API（Stability AI / Photoroom等、未選定） |
| `GOOGLE_DRIVE_CLIENT_ID` | OAuthクライアントID（デスクトップアプリ） |
| `GOOGLE_DRIVE_CLIENT_SECRET` | OAuthクライアントシークレット |
| `GOOGLE_DRIVE_REFRESH_TOKEN` | 上記クライアントで一度だけ認可して得たリフレッシュトークン |
| `DRIVE_FOLDER_ID` | 保存先のGoogleドライブフォルダのID |

## 実行

```
python main.py
```

Claude Code の Routine（毎朝の定期トリガー）から呼び出す想定。
トレンド取得・プロンプト生成・採点・学習分析はこのスクリプトの外側（Claude自身の推論）で行い、
本スクリプトは「生成済みプロンプトを受け取って画像を作る」「選ばれた5枚を補正してDriveに上げる」
という実行部分のみを担当する。

## 現状

まだ画像生成・補正・Drive連携のAPI呼び出しは未実装（雛形のみ）。
実際のAPIキーが揃った段階で `image_gen.py` / `retouch.py` / `drive_upload.py` の
TODO部分を実装する。
