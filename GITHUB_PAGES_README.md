# GitHub Pages 完全自動アフィリエイトシステム

## 📚 概要

**24時間完全自動運営のAIアフィリエイトサイト**を構築するシステムです。

- **完全無料**: GitHub Pagesホスティング（無料）
- **AI記事生成**: Claude 4.5による高品質コンテンツ
- **自動デプロイ**: GitHub Actions で自動公開
- **マネタイズ**: Amazon・楽天アフィリエイト

## 🏗️ システム構成

```
ai-company/
├── docs/                           # GitHub Pages サイト（Jekyll）
│   ├── _config.yml                 # サイト設定
│   ├── _posts/                     # 記事ディレクトリ
│   ├── index.md                    # トップページ
│   └── about.md                    # Aboutページ
├── research/                       # リサーチ部門
│   └── trend_collector.py          # トレンド収集
├── dev/                            # 開発部門
│   └── article_generator_github.py # 記事生成エンジン
├── marketing/                      # マーケティング部門
│   └── github_pages_publisher.py   # 投稿モジュール
├── run_github_pages_automation.py  # メイン実行スクリプト
└── .github/workflows/              # GitHub Actions
    └── jekyll-gh-pages.yml         # 自動デプロイ設定
```

## 🚀 セットアップ手順

### 1. GitHub Pagesを有効化

1. GitHubリポジトリ画面で **Settings** → **Pages**
2. **Source** で `GitHub Actions` を選択
3. **Save** をクリック

### 2. 環境変数を設定

```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

`.bashrc` や `.zshrc` に追加して永続化:

```bash
echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

### 3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

必要なパッケージ:
- `anthropic` - Claude API
- `requests` - HTTP通信
- `python-dateutil` - 日時処理
- `pyyaml` - YAML解析

### 4. アフィリエイトIDを設定（オプション）

`docs/_config.yml` を編集:

```yaml
amazon_affiliate_id: "your-amazon-id-20"
rakuten_affiliate_id: "your-rakuten-id"
```

## 💻 使い方

### テスト実行（1記事のみ生成、投稿スキップ）

```bash
python run_github_pages_automation.py \
  --mode once \
  --max-articles 1 \
  --skip-publish
```

### 本番実行（3記事生成 & 投稿）

```bash
python run_github_pages_automation.py \
  --mode once \
  --max-articles 3
```

### 記事をGitHubに反映

```bash
git add docs/_posts/
git commit -m "Add new articles"
git push origin your-branch
```

プッシュすると、GitHub Actionsが自動でサイトをビルド・デプロイします。

### 24時間自動運用（デーモンモード）

```bash
# 8時間ごとに3記事生成
nohup python run_github_pages_automation.py \
  --mode daemon \
  --interval 8 \
  --max-articles 3 > automation.log 2>&1 &
```

ログ確認:
```bash
tail -f automation.log
```

停止:
```bash
pkill -f run_github_pages_automation.py
```

## 📊 コマンドオプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--mode` | 実行モード (`once` or `daemon`) | `once` |
| `--max-articles` | 生成記事数 | 3 |
| `--category` | カテゴリー (`all`, `AI`, `tech`, `books`) | `all` |
| `--interval` | 実行間隔（時間、daemonモード） | 8 |
| `--skip-publish` | 投稿をスキップ（テスト用） | False |

## 💰 収益化設定

### Amazon アソシエイト

1. [Amazon アソシエイト](https://affiliate.amazon.co.jp/)に登録
2. アソシエイトIDを取得
3. `docs/_config.yml` に設定

### 楽天アフィリエイト

1. [楽天アフィリエイト](https://affiliate.rakuten.co.jp/)に登録
2. アフィリエイトIDを取得
3. `docs/_config.yml` に設定

## 🎯 想定収益

| 項目 | 値 |
|---|---|
| **記事数/月** | 90記事（3記事/日） |
| **想定PV** | 30,000 PV/月 |
| **CVR** | 1% |
| **単価** | 1,500円 |
| **月間収益** | 45,000円 |

※実際の収益は記事品質・SEO順位・商品選定により変動

## 📈 運用コスト

| 項目 | コスト |
|---|---|
| **GitHub Pages** | 無料 |
| **Claude API** | $9-18/月（90記事） |
| **ドメイン（オプション）** | $10-20/年 |
| **合計** | 約$10-20/月 |

**ROI**: 初月から黒字化可能

## 🔧 カスタマイズ

### 記事の文字数を変更

`dev/article_generator_github.py` の `target_length` を編集:

```python
article = generator.generate_article(
    topic=topic,
    keywords=keywords,
    target_length=3000  # ← 変更
)
```

### デザインテーマを変更

`docs/_config.yml` で別のJekyllテーマを指定:

```yaml
theme: jekyll-theme-cayman
```

利用可能なテーマ: https://pages.github.com/themes/

### カテゴリーを追加

`research/trend_collector.py` に新しいカテゴリーを追加。

## 📖 ワークフロー

1. **トレンド収集** (`research/trend_collector.py`)
   - Google Trends、Amazon、楽天から情報収集
   - スコアリング・ランキング

2. **記事生成** (`dev/article_generator_github.py`)
   - Claude 4.5 でSEO記事生成
   - プロンプトキャッシュで高速化・コスト削減

3. **投稿** (`marketing/github_pages_publisher.py`)
   - Jekyll形式で保存
   - Frontmatter + Markdown

4. **デプロイ** (`.github/workflows/jekyll-gh-pages.yml`)
   - GitHub Actions で自動ビルド
   - GitHub Pages に公開

## 🌐 サイトURL

プッシュ後、以下のURLでアクセス可能:

```
https://momonohuz5-sudo.github.io/ai-company/
```

## 🐛 トラブルシューティング

### GitHub Pagesが表示されない

- Settings → Pages で設定確認
- GitHub Actions タブでビルド状況確認
- `docs/_config.yml` の `baseurl` が正しいか確認

### 記事が生成されない

- `ANTHROPIC_API_KEY` が設定されているか確認
- API利用枠の残高確認
- ログで詳細エラーを確認

### ビルドエラー

- `docs/Gemfile` が自動生成されているか確認
- Jekyll の YAML構文エラーをチェック

## 📞 サポート

- GitHub Issues: https://github.com/momonohuz5-sudo/ai-company/issues
- Email: momonohuz5@gmail.com

## 📜 ライセンス

MIT License

---

© 2026 AI Company. Powered by Claude 4.5.
