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
- Phase 4以降（口コミ本文の高度な抽出/整形、AI要約、キャッシュ、デプロイ）は未着手。
- DBはディレクトリのみ用意（ロジック未実装）。

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

## Phase 3: 口コミ検索（men-esthe.jp / 共通Interface）

### 実装内容
- `app/scrapers/base.py`: `ReviewScraper` 共通インターフェース（仕様書37節）
  - サイト追加時にBot本体を変更せずに済むよう、`search_reviews(shop_name, therapist_name) -> list[Review]` のみを要求
- `app/scrapers/men_esthe.py`: Playwrightベースの実装
  - **注意**: men-esthe.jpへの実アクセス許可・HTML構造の確認は未実施のため、セレクタはプレースホルダー。例外時は空リストを返し全体の処理を止めない設計にしている。実運用前に必ず実サイトで検証・調整すること
- `app/models/review.py` / `app/models/search_result.py`: 仕様書38・39節のモデル
- `app/services/search_service.py`: 複数サイトを `asyncio.gather` で並列実行し、サイトごとにタイムアウト（`SCRAPER_TIMEOUT_SECONDS`、デフォルト8秒）を設定。1サイトが失敗/タイムアウトしても他の結果で処理継続（仕様書18・29節）
- Webhookは検索結果を`push_text`でユーザーへ送信（reply tokenは検索の待ち時間中に失効し得るため、仕様書15節の設計通りpushに変更）
  - 0件 → 仕様書26節の「見つけられなかったよ」メッセージ
  - 全サイト失敗 → 仕様書29節の「取得できませんでした」メッセージ
  - 見つかった場合 → 件数を表示（要約はPhase 5で実装予定、暫定メッセージ）

### 動作確認方法
```bash
pytest tests/ -q
```
`tests/test_search_service.py`ではモックScraperで並列実行・タイムアウト・失敗時スキップを検証。
`tests/test_handle_text_message.py`ではWebhookのハンドラ全体のフローを検証。
実サイトへの疎通確認は、許可取得・セレクタ調整後に別途実施する。

### 現在の問題点 / 未実装
- men-esthe.jpの実際のセレクタは未検証（プレースホルダーのまま）。
- AI要約（Phase 5）、キャッシュ（Phase 7）、デプロイ（Phase 8）は未着手。

## Phase 4: 重複除去

### 実装内容
- `app/services/dedup_service.py`: 仕様書22節の重複除去ロジック
  - 前後空白・改行・記号（句読点、感嘆符等）を正規化してから完全一致比較
  - 空文字になった口コミ（記号のみ等）は除外
  - サイトをまたいだ転載も検出（`source`ではなく本文で比較）
  - Embeddingによる類似判定は将来拡張として未実装（構造上追加しやすい形にしてある）
- `search_service.search_all`に組み込み、全サイトの結果を集約後に重複除去してから`SearchResult`を返す

### 動作確認方法
```bash
pytest tests/ -q
```
`tests/test_dedup_service.py`で完全一致・空白差分・記号差分・サイト跨ぎ重複・空文字除外を検証。
`tests/test_search_service.py::test_search_all_dedups_across_sites`で検索パイプライン全体への組み込みを検証。

### 現在の問題点 / 未実装
- 類似度ベース（Embedding）の重複判定は未実装。
- AI要約（Phase 5）、キャッシュ（Phase 7）、デプロイ（Phase 8）は未着手。
