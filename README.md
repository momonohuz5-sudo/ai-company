# AIアフィリエイト記事自動生成システム

Claude APIを活用した完全自動化アフィリエイトマーケティングシステムです。24時間稼働し、トレンド収集→記事生成→自動投稿までを自律的に実行します。

## 🎯 システム概要

### 主な機能

1. **自動トレンド収集** (Research部門)
   - Googleトレンドから急上昇キーワード取得
   - Amazon売れ筋ランキング収集
   - 楽天ランキングAPI連携
   - アフィリエイト適性スコアリング

2. **AI記事生成** (Dev部門)
   - Claude APIによる高品質SEO記事生成
   - 3000文字以上の詳細コンテンツ
   - 自然なアフィリエイトリンク配置
   - プロンプトキャッシュによるコスト最適化

3. **自動投稿** (Marketing部門)
   - WordPress REST API連携
   - 最適な時間帯への自動投稿
   - カテゴリ・タグ自動設定
   - SEOメタデータ自動生成

4. **24時間自動運用** (PM部門)
   - スケジューラーによる定期実行
   - パイプライン全体のオーケストレーション
   - エラーハンドリング・ログ記録
   - パフォーマンス分析

## 📁 ディレクトリ構造

```
ai-company/
├── research/              # トレンド収集・分析
│   ├── trend_collector.py    # トレンド収集モジュール
│   ├── keyword_analyzer.py   # キーワード分析
│   └── data/                 # 収集データ保存先
├── dev/                   # 記事生成・投稿
│   ├── article_generator.py  # AI記事生成エンジン
│   ├── wordpress_publisher.py # WordPress投稿
│   └── articles/             # 生成記事保存先
├── marketing/             # コンテンツ配信・分析
│   ├── content_scheduler.py  # 投稿スケジューラー
│   └── analytics/            # パフォーマンス分析
├── pm/                    # 自動化管理
│   ├── automation_orchestrator.py # オーケストレーター
│   └── logs/                 # システムログ
├── run_automation.py      # メイン実行スクリプト
├── requirements.txt       # Python依存パッケージ
├── .env.example          # 環境変数テンプレート
└── README.md             # このファイル
```

## 🚀 セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` をコピーして `.env` ファイルを作成し、必要な情報を設定します。

```bash
cp .env.example .env
```

#### 必須設定

```env
# Claude API（必須）
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### WordPress投稿用（オプション）

```env
# WordPress設定
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password
```

WordPressアプリケーションパスワードの取得方法:
1. WordPress管理画面 → ユーザー → プロフィール
2. 「アプリケーションパスワード」セクションで新規作成
3. 生成されたパスワードを `WORDPRESS_APP_PASSWORD` に設定

#### アフィリエイト設定（オプション）

```env
# Amazon Associate
AMAZON_ASSOCIATE_TAG=your_amazon_tag
AMAZON_ACCESS_KEY=your_access_key
AMAZON_SECRET_KEY=your_secret_key

# 楽天アフィリエイト
RAKUTEN_AFFILIATE_ID=your_rakuten_id
RAKUTEN_APP_ID=your_rakuten_app_id
```

#### システム設定

```env
# 自動投稿設定
AUTO_POST_ENABLED=false          # true: 自動公開, false: 下書き保存
POST_INTERVAL_HOURS=24           # 実行間隔（時間）
MAX_ARTICLES_PER_DAY=3          # 1日あたりの最大記事数
```

### 3. 環境チェック

```bash
python run_automation.py --check-only
```

## 📖 使い方

### 基本的な使い方

#### 1回のみ実行（テスト）

```bash
# フルサイクル実行（トレンド収集→記事生成→投稿）
python run_automation.py --mode once

# 記事生成のみ（投稿なし）
python run_automation.py --mode once --skip-publish

# 最大3件の記事を生成
python run_automation.py --mode once --max-articles 3
```

#### 24時間自動運用

```bash
# デーモンモードで起動
python run_automation.py --mode daemon
```

バックグラウンド実行（推奨）:

```bash
# nohupで起動
nohup python run_automation.py --mode daemon > automation.log 2>&1 &

# スクリーンセッションで起動
screen -S affiliate-automation
python run_automation.py --mode daemon
# Ctrl+A → D でデタッチ

# プロセス確認
ps aux | grep run_automation.py
```

### 個別モジュールの実行

#### トレンド収集のみ

```bash
cd research
python trend_collector.py
```

#### 記事生成のみ

```bash
cd dev
python article_generator.py
```

#### WordPress接続テスト

```bash
cd dev
python wordpress_publisher.py
```

## 🔧 カスタマイズ

### 記事生成のカスタマイズ

`dev/article_generator.py` の `create_article_prompt()` メソッドでプロンプトを調整できます。

```python
# 記事の文字数変更
target_length = 5000  # デフォルト: 3000

# 記事構成のカスタマイズ
# create_article_prompt() 内のプロンプトを編集
```

### アフィリエイトスコアの調整

`research/keyword_analyzer.py` の `calculate_affiliate_score()` メソッドで評価基準を変更できます。

```python
# スコア閾値の変更
min_score = 70.0  # デフォルト: 60.0

# カテゴリの追加
HIGH_VALUE_CATEGORIES = [
    '美容', 'ダイエット', 'ガジェット',
    'あなたのカテゴリ'  # 追加
]
```

### 投稿スケジュールの変更

`marketing/content_scheduler.py` の `generate_optimal_schedule()` で投稿タイミングを調整できます。

```python
# 最適な投稿時間帯
optimal_hours = [9, 12, 15, 20]  # お好みの時間に変更

# 投稿間隔
posts_per_day = 2  # 1日あたりの投稿数
```

## 📊 パフォーマンス分析

生成された記事のパフォーマンスを追跡できます。

```python
from marketing.content_scheduler import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# 記事のメトリクス記録
analyzer.track_article_performance(
    article_id='article_001',
    metrics={
        'page_views': 1500,
        'affiliate_clicks': 45,
        'conversions': 3
    }
)

# レポート生成
report = analyzer.generate_performance_report()
print(report)
```

## 💰 コスト見積もり

### Claude API利用料（目安）

- **1記事あたり**: 約$0.10〜$0.20（3000文字）
- **1日3記事**: 約$0.30〜$0.60
- **月間コスト**: 約$9〜$18（90記事/月）

プロンプトキャッシュを使用することで、コストをさらに削減できます。

### 収益化の例

- **月間90記事** × **月間PV 500/記事** = **45,000PV/月**
- **CTR 5%** × **成約率 2%** = **45件の成約/月**
- **報酬単価 1,000円** → **月間45,000円の収益**

**ROI**: 45,000円（収益） - 1,800円（コスト） = **43,200円の利益/月**

## 🛡️ セキュリティ

- `.env` ファイルは **絶対に** Gitにコミットしないでください
- `.gitignore` で以下を除外:
  ```
  .env
  *.json  # APIキーを含むファイル
  articles/
  data/
  logs/
  ```

## 🐛 トラブルシューティング

### Claude API接続エラー

```
ValueError: ANTHROPIC_API_KEY が設定されていません
```

→ `.env` ファイルに `ANTHROPIC_API_KEY` を設定してください

### WordPress投稿エラー

```
WordPress接続失敗: 401
```

→ アプリケーションパスワードが正しいか確認してください

### トレンド収集エラー

```
Google Trends収集エラー
```

→ ネットワーク接続を確認してください（一時的なAPI制限の可能性もあります）

## 📝 ログ確認

システムログは以下に保存されます:

- `pm/logs/pipeline_logs.json` - パイプライン実行ログ
- `pm/logs/error_logs.json` - エラーログ
- `dev/publish_logs/publish_history.json` - 投稿履歴

## 🔄 アップデート

```bash
# 最新のコードを取得
git pull origin main

# 依存パッケージの更新
pip install -r requirements.txt --upgrade
```

## 📞 サポート

問題が発生した場合は、以下を確認してください:

1. 環境変数が正しく設定されているか
2. 依存パッケージがインストールされているか
3. ネットワーク接続が安定しているか
4. Claude APIの利用制限に達していないか

## 📄 ライセンス

このプロジェクトはAI Companyの内部プロジェクトです。

## 🎉 貢献

各部門の担当者は、自部門のディレクトリ内でモジュールを改善してください。

- Research部門: `research/`
- Dev部門: `dev/`
- Marketing部門: `marketing/`
- PM部門: `pm/`

変更を加える際は、必ず各部門の `CLAUDE.md` に従ってください。

---

**開発者**: AI Company全部門協力プロジェクト  
**最終更新**: 2026-05-27
