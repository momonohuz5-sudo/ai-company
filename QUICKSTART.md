# 🚀 クイックスタートガイド

AIアフィリエイト記事自動生成システムを5分で始める方法

## ステップ1: 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## ステップ2: 環境変数の設定

### 最小構成（ローカルテスト）

`.env` ファイルを作成:

```bash
# Claude API（必須）
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

これだけで記事生成まで動作します！（記事はローカルに保存されます）

### WordPress投稿も試す場合

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# WordPress
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

## ステップ3: 動作確認

### テスト実行（記事生成のみ）

```bash
python run_automation.py --mode once --skip-publish --max-articles 1
```

これで以下が実行されます:
1. ✅ トレンド収集
2. ✅ キーワード分析
3. ✅ 記事生成（1件）

生成された記事は `dev/articles/` に保存されます。

### WordPress投稿テスト

```bash
python run_automation.py --mode once --max-articles 1
```

`.env` に WordPress設定があれば、自動的に投稿されます（下書き保存）。

## ステップ4: 24時間自動運用

```bash
# バックグラウンドで実行
nohup python run_automation.py --mode daemon > automation.log 2>&1 &
```

設定した間隔で自動的に:
1. トレンド収集
2. 記事生成
3. WordPress投稿

が繰り返し実行されます。

## 📊 生成結果の確認

### 記事ファイル

```bash
ls -l dev/articles/
```

各記事は以下の形式で保存されます:
- `YYYYMMDD_HHMMSS_キーワード.json` - メタデータ
- `YYYYMMDD_HHMMSS_キーワード.md` - Markdown版

### ログ確認

```bash
# パイプラインログ
cat pm/logs/pipeline_logs.json

# エラーログ
cat pm/logs/error_logs.json

# 投稿履歴
cat dev/publish_logs/publish_history.json
```

## ⚙️ よく使う設定

### 自動公開を有効化

`.env`:
```bash
AUTO_POST_ENABLED=true  # 下書きではなく即公開
```

### 投稿頻度の変更

`.env`:
```bash
POST_INTERVAL_HOURS=12   # 12時間ごと（デフォルト: 24）
MAX_ARTICLES_PER_DAY=5   # 1日5記事（デフォルト: 3）
```

## 🎯 次のステップ

1. **アフィリエイトリンクの設定**
   - Amazon Associate タグ取得
   - 楽天アフィリエイト登録

2. **記事品質の向上**
   - プロンプトのカスタマイズ (`dev/article_generator.py`)
   - キーワードフィルタの調整 (`research/keyword_analyzer.py`)

3. **パフォーマンス分析**
   - Google Analytics連携
   - アフィリエイト成果の追跡

詳細は `README.md` をご覧ください！

---

**トラブル?** → `python run_automation.py --check-only` で環境チェック
