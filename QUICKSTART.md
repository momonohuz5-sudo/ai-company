# 🚀 クイックスタートガイド

**5分で始める GitHub Pages 完全自動アフィリエイトシステム**

## ⚡ 最速セットアップ

### 1️⃣ GitHub Pages を有効化（1分）

1. GitHubリポジトリページを開く
2. **Settings** → **Pages** をクリック
3. **Source** で `GitHub Actions` を選択
4. **Save** をクリック

✅ これで自動デプロイの準備完了！

### 2️⃣ APIキーを設定（1分）

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

> **APIキーの取得方法**: [Claude Console](https://console.anthropic.com/) でアカウント作成 → API Keys

### 3️⃣ テスト実行（3分）

```bash
# パッケージインストール
pip install anthropic requests python-dateutil pyyaml

# 1記事だけ生成してテスト（投稿はしない）
python run_github_pages_automation.py --mode once --max-articles 1 --skip-publish
```

**成功すると**:
```
✅ 記事生成完了: Claude 4.5の新機能と活用方法
🔍 [テストモード] 保存をスキップ
```

### 4️⃣ 本番実行 & 公開（1分）

```bash
# 3記事を生成して投稿
python run_github_pages_automation.py --mode once --max-articles 3

# GitHubに反映
git add docs/_posts/
git commit -m "Add initial articles"
git push origin your-branch
```

### 5️⃣ サイト確認

5-10分後、以下のURLで公開されます:

```
https://momonohuz5-sudo.github.io/ai-company/
```

---

## 🎉 おめでとうございます！

あなたのAI自動アフィリエイトサイトが完成しました！

## 📖 次のステップ

### 定期自動運用を開始

```bash
# 8時間ごとに3記事を自動生成
nohup python run_github_pages_automation.py --mode daemon --interval 8 --max-articles 3 > automation.log 2>&1 &
```

### アフィリエイトIDを設定

`docs/_config.yml` を編集:

```yaml
amazon_affiliate_id: "your-amazon-id-20"
rakuten_affiliate_id: "your-rakuten-id"
```

### カスタマイズ

詳しくは [GITHUB_PAGES_README.md](./GITHUB_PAGES_README.md) を参照。

---

## 💡 ヒント

- **記事数を増やす**: `--max-articles 5` で5記事生成
- **カテゴリー指定**: `--category AI` でAI記事のみ
- **ログ確認**: `tail -f automation.log` でリアルタイム監視

## ❓ 困ったら

- [README](./GITHUB_PAGES_README.md) のトラブルシューティング参照
- [GitHub Issues](https://github.com/momonohuz5-sudo/ai-company/issues)

---

Happy Automating! 🤖💰
