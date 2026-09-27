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
- キャッシュ（Phase 7）、デプロイ（Phase 8）は未着手。

## Phase 5: AI要約（Google Gemini API）

仕様書ではOpenAI APIを想定していたが、運用コストを抑えるため無料枠のある
**Google Gemini API**（`gemini-3.8-flash`）を採用（ユーザー確認済み）。
将来OpenAI等へ切り替える場合も、`Summarizer`インターフェースの差し替えだけで済む構造にしてある。

### 実装内容
- `app/prompts/summary_prompt.txt`: 仕様書24節のシステムプロンプト＋40節のJSON出力形式
- `app/services/summarizer.py`: `Summarizer`共通インターフェース、プロンプト組み立て
- `app/services/gemini_summarizer.py`: Gemini REST APIを`httpx`で呼び出し、JSON応答をパース（```json``` フェンス除去にも対応）
- `app/models/summary.py`: `SummaryResult(review_count, summary_points, mixed_opinion)`
- `app/services/message_builder.py`: 仕様書5節・41節の件数別クロージング文言を生成
  - 1件：「こんな口コミがみられたよ！」
  - 2〜3件：「複数の口コミで〜という声が…」
  - 4件以上：「という口コミが多くみられたよ！」
  - 評価が分かれている場合：「評価が分かれているみたい！」
- Webhookに統合。要約失敗時は仕様書29節の「取得できませんでした」メッセージにフォールバック

### 必要な環境変数（追加）
- `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com/)で無料発行
- `GEMINI_MODEL`（デフォルト`gemini-3.8-flash`）

### 動作確認方法
```bash
pytest tests/ -q
```
`tests/test_message_builder.py`で件数別の文言分岐、`tests/test_gemini_summarizer.py`でプロンプト組み立て・JSONパース（コードフェンス対応含む）、
`tests/test_handle_text_message.py`で要約成功/失敗時のWebhook全体フローを検証。
実際のAPI呼び出し確認は`GEMINI_API_KEY`設定後に別途実施する。

### 現在の問題点 / 未実装
- Gemini無料枠のレート制限に達した場合のリトライ/待機処理は未実装。
- デプロイ（Phase 8）は未着手。

## Phase 7: SQLiteキャッシュ

### 実装内容
- `app/db/models.py`: 仕様書21節の`search_cache`・`reviews`テーブル（SQLAlchemy ORM）
- `app/db/database.py`: 非同期エンジン/セッション、`init_db()`でテーブル自動作成
- `app/services/cache_service.py`
  - `get_cached_message(shop_name, therapist_name)`: 有効期限内（`expires_at > 現在時刻`）のキャッシュがあれば要約メッセージをそのまま返す
  - `save_cache(...)`: `CACHE_TTL_SECONDS`（デフォルト6時間）後に失効するレコードを保存
  - `save_reviews(...)`: 口コミ本文・出典URL・取得日時を内部保存用に記録（ユーザーには非表示、仕様書21・34節）
- Webhookに統合
  - 検索前にキャッシュを確認し、ヒットすればWeb検索・AI要約をスキップして即push（目標3秒以内）
  - 検索結果（0件の場合も含む）をキャッシュに保存し、同じ組み合わせへの再アクセス負荷を抑制（仕様書33節）
- `app/main.py`: FastAPIのlifespanで起動時に`init_db()`を実行しテーブルを作成

### 動作確認方法
```bash
pytest tests/ -q
```
`tests/test_cache_service.py`でインメモリSQLiteを使い、キャッシュヒット/ミス/他セラピストとの非混同/期限切れを検証。
`tests/test_handle_text_message.py::test_cache_hit_skips_search_and_pushes_cached_message`でWebhook全体のキャッシュ短絡フローを検証。

### 現在の問題点 / 未実装
- 本番ではSQLiteからPostgreSQLへの移行を想定（`DATABASE_URL`を変更するだけで対応できる設計）。

## Phase 8: クラウドデプロイ（Google Cloud Run）

開発者PC非依存（仕様書13節）を満たすため、Google Cloud Runへのデプロイを想定。
Playwright（Chromium）をコンテナに含める必要があるため、公式イメージ`mcr.microsoft.com/playwright/python`をベースにしている。

### 実装内容
- `Dockerfile`: Playwright公式イメージベース（Chromium同梱、apt依存の手動管理が不要）。`playwright`のバージョンをベースイメージのタグ（v1.47.0）に固定してChromiumとの不一致を防止
- `.dockerignore`: `.env`・テスト・開発用ファイルを除外
- Cloud Runは`PORT`環境変数を自動注入するため、`CMD`はそれを読んでuvicornを起動する構成

### デプロイ手順（gcloud CLIが使える環境で実行）
```bash
# 1. Google Cloudプロジェクトを設定
gcloud config set project <YOUR_PROJECT_ID>

# 2. Artifact Registry等へビルド&デプロイ（ソースから直接）
gcloud run deploy line-esthe-bot \
  --source . \
  --region asia-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 30 \
  --set-env-vars "GEMINI_MODEL=gemini-3.8-flash,CACHE_TTL_SECONDS=21600,SCRAPER_TIMEOUT_SECONDS=8"

# 3. Secret（トークン類）はSecret Managerで管理し、--set-secrets で注入するのが推奨（直書き厳禁、仕様書31節）
gcloud secrets create line-channel-access-token --data-file=- <<< "<TOKEN>"
gcloud secrets create line-channel-secret --data-file=- <<< "<SECRET>"
gcloud secrets create gemini-api-key --data-file=- <<< "<GEMINI_KEY>"

gcloud run services update line-esthe-bot \
  --region asia-northeast1 \
  --set-secrets "LINE_CHANNEL_ACCESS_TOKEN=line-channel-access-token:latest,LINE_CHANNEL_SECRET=line-channel-secret:latest,GEMINI_API_KEY=gemini-api-key:latest"

# 4. デプロイ完了後に発行されるURL（https://xxx-yyy.a.run.app）の末尾に /webhook を付けて
#    LINE Developersコンソールの Webhook URL に設定する
```

- SQLiteはCloud Runのコンテナ再起動でリセットされる（永続ディスクではないため）。本番運用では`DATABASE_URL`をCloud SQL(PostgreSQL)等に向けるだけで移行可能な設計にしてある（仕様書12節）
- Cloud Runはリクエスト処理中のみ課金されるため、運用コストを抑えられる（仕様書45節の最優先事項に合致）

### 動作確認方法
このクラウド環境（Claude Codeのセッション）にはDockerデーモンがないため、`docker build`によるローカル検証はできていない。
デプロイ実行者の手元、またはCloud Build（`gcloud run deploy --source .`は自動でCloud Buildを使う）でのビルド確認が必要。
デプロイ後は、LINE公式アカウントへ「店舗名 セラピスト名」を送信し、15秒前後で要約が返ってくることを確認する。

### 現在の問題点 / 未実装
- Dockerビルドの実機検証は未実施（環境制約のため）。
- Cloud Run最小インスタンス数を0にした場合のコールドスタート（Playwright起動込みで数秒〜十数秒）は考慮が必要。応答性重視なら`--min-instances 1`を検討。

## 追加対応: アクセス負荷対策（仕様書33節）

- `app/services/search_service.py`: `asyncio.Semaphore`で同時スクレイピング数の上限を設定（デフォルト3、`MAX_CONCURRENT_SCRAPES`で変更可）。複数ユーザーから同時にメッセージが来ても、対象サイトへの同時アクセス数が青天井にならないようにしている
- 同一人物への検索はPhase 7のキャッシュで既に抑制済み

## 追加対応: CI

`.github/workflows/line-esthe-bot-tests.yml`で、`dev/line-esthe-bot/`配下への変更時に自動でテストを実行する（Playwrightの実ブラウザは使わずモックでテストしているため、CIでのブラウザインストールは不要）。

## menethesteサイトアクセスについて

men-esthe.jpの実アクセスには課金が必要とのことで、実際のセレクタ検証・実スクレイピング動作確認は別途準備が整い次第実施する。それまでは`app/scrapers/men_esthe.py`のプレースホルダーセレクタのままとなる。
