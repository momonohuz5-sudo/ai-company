# LINE メンズエステ口コミ要約Bot

仕様書に基づく実装。Phase 1〜順番に実装する。

## Phase 1: LINE接続（固定メッセージ返信）

### 実装内容
- FastAPI アプリ (`app/main.py`)
- LINE Webhook受信エンドポイント (`app/line/webhook.py`)
  - `X-Line-Signature` を検証（HMAC-SHA256）
  - テキストメッセージ受信時、固定文言でリプライ（バックグラウンドタスクで非同期実行し、Webhookは即200を返す）
- LINE Messaging API クライアント (`app/line/client.py`): reply/push実装

### 必要な環境変数（`.env.example` 参照）
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `OPENAI_API_KEY`（Phase 5以降で使用）
- `DATABASE_URL`（Phase 7以降で使用、デフォルトSQLite）
- `CACHE_TTL_SECONDS`（デフォルト6時間）
- `SCRAPER_TIMEOUT_SECONDS`（デフォルト8秒）

### 動作確認方法
```bash
pip install -r requirements.txt
cp .env.example .env  # 値を設定
uvicorn app.main:app --reload
pytest tests/ -q
```
LINE Developers コンソールでWebhook URLを `https://<host>/webhook` に設定し、
公式アカウントへメッセージを送ると固定文言が返信される。

### 現在の問題点 / 未実装
- Phase 3以降（口コミ検索、AI要約、キャッシュ、デプロイ）は未着手。
- DB・スクレイパーはディレクトリのみ用意（ロジック未実装）。

## Phase 2: 入力解析（店舗名 + セラピスト名）

### 実装内容
- `app/services/parser_service.py`: 簡易パーサー
  - スペース/改行区切り（`ABC新宿 あい` / `ABC新宿\nあい`）
  - 「の」区切り（`ABC新宿のあい`）
  - 単一トークンのみ（店舗名なし）→ `MISSING_SHOP`
  - 空文字・解析不能 → `UNPARSEABLE`
- `app/models/parsed_query.py`: `ParsedQuery(shop_name, therapist_name)`
- Webhookは解析結果に応じて仕様書ルール27・28のメッセージを返信
  - 成功時は現時点では検索前の確認メッセージのみ（Phase 3で実検索に接続）

### 動作確認方法
```bash
pytest tests/ -q
```
LINEから `ABC新宿 あい` 等を送信し、店舗名・セラピスト名が正しく解析されて
返信されることを確認する。
