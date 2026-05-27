# GitHub Pages アフィリエイト自動化システム

24時間自動でAIがアフィリエイト記事を生成し、GitHub Pagesで公開する完全無料システムです。

## 🎯 特徴

- ✅ **完全無料**: GitHub Pages利用（無料枠）
- ✅ **自動生成**: Claude APIで高品質記事を自動作成
- ✅ **自動公開**: Git pushで自動的にサイト更新
- ✅ **SEO最適化**: Jekyll + プラグインでSEO対応
- ✅ **レスポンシブ**: モバイル対応デザイン

## 📁 構成

```
ai-company/
├── docs/                          # GitHub Pagesサイト本体
│   ├── _config.yml               # Jekyll設定
│   ├── _posts/                   # 記事ディレクトリ（自動生成）
│   ├── index.md                  # トップページ
│   ├── about.md                  # Aboutページ
│   └── Gemfile                   # Ruby依存関係
├── .github/workflows/
│   └── jekyll-gh-pages.yml       # 自動デプロイ設定
├── dev/
│   └── article_generator_github.py  # 記事生成エンジン
├── marketing/
│   └── github_pages_publisher.py    # 投稿モジュール
└── run_github_pages_automation.py   # メイン実行スクリプト
```

## 🚀 セットアップ

### 1. リポジトリ設定

```bash
# このブランチをmainにマージ、またはGitHub Pagesのソースブランチに設定
git checkout main
git merge claude/slack-session-Bds42
git push origin main
```

### 2. GitHub Pagesを有効化

1. GitHubリポジトリの Settings → Pages
2. **Source**: `GitHub Actions` を選択
3. **Branch**: `main` を選択（または現在のブランチ）
4. 保存

### 3. 環境変数設定

```bash
# .env ファイルを作成
cat > .env << EOF
ANTHROPIC_API_KEY=your_api_key_here
EOF
```

### 4. Pythonパッケージインストール

```bash
pip install anthropic
```

## 📝 使い方

### テスト実行（1記事のみ生成）

```bash
python run_github_pages_automation.py --mode once --max-articles 1
```

### 複数記事生成

```bash
python run_github_pages_automation.py --mode once --max-articles 3
```

### 24時間自動運用（1時間ごとに3記事生成）

```bash
nohup python run_github_pages_automation.py --mode daemon --interval 3600 --max-articles 3 > automation.log 2>&1 &
```

### Git push してサイト公開

```bash
git add docs/_posts/
git commit -m "Add new articles"
git push origin main
```

GitHub Actionsが自動でビルド・デプロイを実行します（2-3分）。

## 🌐 サイトURL

デプロイ後、以下のURLでアクセス可能：

```
https://<username>.github.io/ai-company/
```

例: `https://momonohuz5-sudo.github.io/ai-company/`

## 📊 カスタマイズ

### サイト情報変更

`docs/_config.yml` を編集：

```yaml
title: あなたのサイト名
description: サイトの説明
author: あなたの名前
```

### アフィリエイトリンク設定

`run_github_pages_automation.py` の `get_sample_articles()` 関数内で商品情報を設定：

```python
"affiliate_products": [
    {
        "name": "商品名",
        "url": "https://amazon.co.jp/dp/XXXXX?tag=your-id",
        "description": "商品説明"
    }
]
```

### 記事トピック変更

`get_sample_articles()` 関数で自由に設定可能：

```python
{
    "topic": "あなたのトピック",
    "keywords": ["キーワード1", "キーワード2"],
    "categories": ["カテゴリ"],
    "tags": ["タグ1", "タグ2"]
}
```

## 💰 コスト試算

| 項目 | 月間コスト |
|---|---|
| GitHub Pages | 無料 |
| Claude API (90記事/月) | $9-18 |
| **合計** | **$9-18** |

想定収益: 月4万円以上 → **ROI 200%以上**

## 🔧 トラブルシューティング

### サイトが表示されない

1. GitHub Actions のログを確認
2. `docs/_posts/` に記事ファイルが存在するか確認
3. GitHub Pages設定でソースが正しく選択されているか確認

### 記事生成エラー

```bash
# ログ確認
tail -f github_pages_automation.log

# APIキーが設定されているか確認
echo $ANTHROPIC_API_KEY
```

## 📈 次のステップ

選択肢Bが成功したら、選択肢A（note/はてなブログ/Medium自動投稿）も実装可能です！

---

**AI Company - 完全自動アフィリエイトシステム** 🤖
