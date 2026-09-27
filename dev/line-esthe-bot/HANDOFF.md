# 引き継ぎドキュメント（Claude → Codex）

最終更新: 2026-09-27
ブランチ: `claude/gallant-thompson-46yyku`
テスト状況: `pytest tests/ -q` で **38件全通過**

---

## 1. プロジェクト概要

LINE公式アカウントに「店舗名 + セラピスト名」を送ると、Web上の口コミを収集・AI要約してLINEへ返信するBot。
元仕様書は `/home/user/ai-company/CLAUDE.md` のプロジェクトルートに貼られたメッセージ（本ドキュメント末尾に全文転記）。

最優先事項（仕様書45節）：
1. シンプルで壊れにくい
2. 15秒前後で返信する
3. 開発者PCに依存しない（すべてクラウド実行）
4. 口コミ内容を捏造しない
5. サイト追加が容易
6. 運用コストを低くする

---

## 2. 実装済みフェーズ（Phase 1〜8、Phase 6はPhase5に統合）

| Phase | 内容 | 状態 |
|---|---|---|
| 1 | LINE Webhook受信・署名検証・固定返信 | ✅完了 |
| 2 | 店舗名+セラピスト名の入力解析（簡易パーサー） | ✅完了 |
| 3 | 口コミ検索（`ReviewScraper`共通Interface＋men-esthe.jpスクレイパー） | ⚠️**実装済みだがセレクタはプレースホルダー**（後述） |
| 4 | 重複除去（完全一致＋空白/改行/記号正規化） | ✅完了 |
| 5 | AI要約（**OpenAIではなくGoogle Gemini API採用**、後述） | ✅完了・実API疎通確認済み |
| 7 | SQLiteキャッシュ（`search_cache`/`reviews`テーブル） | ✅完了 |
| 8 | クラウドデプロイ設定（Dockerfile、Cloud Run向け手順） | ⚠️**Dockerfileは作成済みだが実ビルド未検証**（後述） |

各PhaseごとのREADME内訳は `README.md` を参照（実装内容・環境変数・動作確認方法・既知の問題点をPhaseごとに記載済み）。

---

## 3. 仕様書からの変更点（要合意事項の確認）

1. **AI要約はOpenAIではなくGoogle Gemini API（無料枠）を使用**
   - 理由：ユーザーが運用コストを抑えたいと明言、無料枠があり日本語品質も良いため
   - `app/services/summarizer.py`の`Summarizer`インターフェース経由なので、OpenAI等への切り替えは実装差し替えのみで可能
   - モデル名は当初`gemini-2.0-flash`を指定していたが、**2026-09-27時点で廃止されており`gemini-3.8-flash`に変更済み**（要注意：Codex側でも今後モデルの生存確認が必要になる可能性あり）
   - `OPENAI_API_KEY`は`config.py`に残してあるが未使用（将来の切り替え用）

2. **デプロイ先はGoogle Cloud Run**（Railway・Google Apps Scriptも検討したが却下）
   - GAS却下理由：`UrlFetchApp`はJS実行不可のためPlaywright（ヘッドレスブラウザ）が使えない。men-esthe.jpはログイン必須ページのため、Google検索グラウンディング（Geminiのweb検索ツール）でも代替不可なことを実際にAPIで検証済み（会員限定コンテンツは検索エンジンにインデックスされていないため空振りした）
   - Railway却下理由：無料枠が小さくPlaywright常駐だとすぐ有料化、日本リージョンがなくレイテンシ不利
   - Cloud Run採用理由：無料枠が大きい、東京リージョンあり、Dockerコンテナをそのまま動かせる、Secret Manager連携、将来のCloud SQL移行が容易

3. **アクセス負荷対策（仕様書33節）として`asyncio.Semaphore`を追加**
   - `app/services/search_service.py`で同時スクレイピング数を`MAX_CONCURRENT_SCRAPES`（デフォルト3）に制限

---

## 4. 最優先の未完了タスク（Codexが最初に着手すべきこと）

### 4-1. men-esthe.jpへの実アクセス・スクレイパー実装（最優先）

**現状**：`app/scrapers/men_esthe.py`のセレクタは全てプレースホルダー（`input[type=search]`等の推測値）。実サイトへのアクセス許可・会員登録が必要なため未検証。

ユーザーからの情報：
- men-esthe.jpは**課金（会員登録）しないと口コミ本文が読めない**
- ユーザーが課金・アカウント準備を進める予定（本ドキュメント作成時点で未完了）
- ログインが必要なため、Playwrightでの認証付きスクレイピングが必須（Gemini検索等での代替は技術的に不可能なことを検証済み）

**Codexへの依頼事項**：
1. ユーザーからmen-esthe.jpのログイン情報（ID/PW）と実際のページHTML構造を受け取る
2. `app/scrapers/men_esthe.py`の`SEARCH_INPUT_SELECTOR`等のプレースホルダーセレクタを実物に差し替え
3. ログイン処理を追加（仕様書32節：認証情報はSecret Manager等サーバー側で管理、直書き禁止、Cookie失効時のエラーログ、無限リトライ禁止）
4. 環境変数`MEN_ESTHE_LOGIN_ID` / `MEN_ESTHE_LOGIN_PASSWORD`のような形で`config.py`に追加することを推奨
5. 実サイトでの動作確認（1〜2件のテスト検索で口コミが取得できるか）

### 4-2. Cloud Runへの実デプロイ

**現状**：`Dockerfile`は作成済みだが、**このセッションの環境にはDockerデーモンがなかったため`docker build`によるローカル検証が未実施**。

**Codexへの依頼事項**：
1. `docker build .`が通ることを確認（Playwright公式イメージ`mcr.microsoft.com/playwright/python:v1.47.0-jammy`ベース）
2. README.md「Phase 8」セクションに記載の`gcloud run deploy`手順を実行（ユーザーのGCPプロジェクトが必要、ユーザーの手元 or Codex環境で）
3. Secret Manager経由でLINE/Geminiの認証情報を設定
4. デプロイ後のURLをLINE Developersコンソールの Webhook URL に設定
5. 実際にLINEでメッセージを送って、受信→解析→検索→要約→返信の一連のフローを確認

### 4-3. Geminiモデル名の再確認

`gemini-3.8-flash`は2026-09-27のAPI疎通確認で得られた最新モデル名。Codex側で再度実行するタイミングでさらに新しいモデルにリプレースされている可能性があるため、デプロイ前に以下で疎通確認すること：

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}'
```
404が返る場合、エラーメッセージに新しいモデル名が示唆されるのでそれに追従する。

---

## 5. 秘密情報の状態

ユーザーから以下を受領し、`.env`（Git管理外）に設定済み・動作確認済み：

- `LINE_CHANNEL_ACCESS_TOKEN`：有効性確認済み（`/v2/bot/info`で`口コミbot`/`@853yzrwb`を確認）
- `LINE_CHANNEL_SECRET`：設定済み
- `GEMINI_API_KEY`：有効性確認済み（実際に要約生成に成功）

**Codexへの注意**：これらの値は本ドキュメントやコミット履歴には一切含めていない。`.env`ファイル（このワークスペース内、Git管理外）を直接参照するか、ユーザーに再度確認すること。新しい環境（別のコンテナ・別のCodexセッション）で作業する場合は、ユーザーに値の再共有を依頼する必要がある。

---

## 6. ディレクトリ構成

```
dev/line-esthe-bot/
├── app/
│   ├── main.py                    # FastAPIエントリポイント（lifespanでinit_db）
│   ├── config.py                  # 環境変数読み込み
│   ├── line/
│   │   ├── webhook.py             # Webhook受信・全体オーケストレーション
│   │   └── client.py              # LINE reply/push API呼び出し
│   ├── services/
│   │   ├── parser_service.py      # 店舗名+セラピスト名パーサー
│   │   ├── search_service.py      # 複数スクレイパー並列実行＋Semaphore制限
│   │   ├── dedup_service.py       # 口コミ重複除去
│   │   ├── summarizer.py          # Summarizer抽象インターフェース＋プロンプト組立
│   │   ├── gemini_summarizer.py   # Gemini実装
│   │   ├── message_builder.py     # 件数別LINE返信文言生成
│   │   └── cache_service.py       # SQLiteキャッシュ読み書き
│   ├── scrapers/
│   │   ├── base.py                # ReviewScraper共通インターフェース
│   │   └── men_esthe.py           # ⚠️セレクタ未検証・要実装
│   ├── models/                    # dataclass群（Review, SearchResult, SummaryResult, ParsedQuery）
│   ├── db/
│   │   ├── database.py            # 非同期SQLAlchemyエンジン/セッション
│   │   └── models.py              # search_cache / reviews テーブル定義
│   ├── prompts/
│   │   └── summary_prompt.txt     # Gemini向けシステムプロンプト
│   └── utils/logger.py
├── tests/                         # 38件、pytest-asyncio使用
├── Dockerfile                     # Playwright公式イメージベース（未ビルド検証）
├── .dockerignore
├── requirements.txt
├── .env.example
├── .env                           # Git管理外・実際の値入り
├── pytest.ini
└── README.md                      # Phaseごとの詳細実装ログ
```

CI: `.github/workflows/line-esthe-bot-tests.yml`（`dev/line-esthe-bot/`配下変更時に自動テスト）

---

## 7. 動作確認方法（Codexがまず実行すべきコマンド）

```bash
cd dev/line-esthe-bot
pip install -r requirements.txt
pytest tests/ -q   # 38 passed が出ることを確認

# .envが存在することを確認（実際の値が入っている）
cat .env

# Gemini疎通確認
set -a && source .env && set +a
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" -d '{"contents":[{"parts":[{"text":"test"}]}]}'

# LINE疎通確認
curl "https://api.line.me/v2/bot/info" -H "Authorization: Bearer ${LINE_CHANNEL_ACCESS_TOKEN}"
```

---

## 8. 元仕様書全文

元の仕様書はプロジェクトルート直下の会話に貼られたテキストで、このリポジトリ内に単独ファイルとしては存在しない。
主要ルールの参照先（本ドキュメント中で「仕様書X節」と書いている番号）は、ユーザーが最初にClaude Codeへ貼り付けた
「LINE メンズエステ口コミ要約Bot MVP仕様書」（全45節＋Cursor向け指示）を指す。Codexへの引き継ぎ時にユーザーへ
原文の再共有を依頼するか、このセッションの会話ログを参照すること。

要点のみ再掲：
- 入力：「店舗名 + セラピスト名」（表記ゆれ許容）
- 出力：3〜5項目の箇条書き要約＋件数に応じた文末表現（1件/2-3件/十分/評価割れ）
- 口コミ本人について断定しない、第三者の主観として表現する
- 出典URLはユーザーに非表示、DB内部保存のみ
- スクリーンショット機能は実装しない
- サイトごとにスクレイパーを分離、共通形式に変換
- キャッシュ：`shop_name`+`therapist_name`キー、6時間TTL
- タイムアウト：1サイト5〜8秒、失敗時はスキップして他の結果で継続
- 開発者PC非依存、すべてクラウド実行（Playwrightもheadless）
- Secret類は.envまたはSecret Manager、直書き禁止
