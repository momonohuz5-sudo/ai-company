# ポーカー戦略note自動投稿システム - クイックスタート

## 🚀 ワンコマンドセットアップ

### Windows

1. **リポジトリをダウンロード**
```cmd
git clone https://github.com/momonohuz5-sudo/ai-company.git
cd ai-company\dev\poker-note-generator
```

2. **自動セットアップ実行**（ダブルクリックでOK）
```cmd
setup.bat
```

3. **.envファイルを編集**
```cmd
notepad .env
```

以下を設定:
- `ANTHROPIC_API_KEY`: あなたのClaude APIキー
- `NOTE_EMAIL`: momonohuz5@gmail.com
- `NOTE_PASSWORD`: あなたのnoteパスワード
- `NOTE_USER_URLNAME`: poker_jp

4. **テスト投稿**
```cmd
venv\Scripts\activate
python main.py post-real
```

5. **完全自動化**
```cmd
start_scheduler.bat
```

**完了！** 毎日午前9時に自動投稿されます 🎉

---

### Mac / Linux

1. **リポジトリをダウンロード**
```bash
git clone https://github.com/momonohuz5-sudo/ai-company.git
cd ai-company/dev/poker-note-generator
```

2. **自動セットアップ実行**
```bash
bash setup.sh
```

3. **.envファイルを編集**
```bash
nano .env
```

以下を設定:
- `ANTHROPIC_API_KEY`: あなたのClaude APIキー
- `NOTE_EMAIL`: momonohuz5@gmail.com
- `NOTE_PASSWORD`: あなたのnoteパスワード
- `NOTE_USER_URLNAME`: poker_jp

4. **テスト投稿**
```bash
source venv/bin/activate
python main.py post-real
```

5. **完全自動化**
```bash
chmod +x start_scheduler.sh
./start_scheduler.sh
```

**完了！** 毎日午前9時に自動投稿されます 🎉

---

## 📋 たった5ステップ

| ステップ | 内容 | 所要時間 |
|----------|------|----------|
| 1 | リポジトリクローン | 1分 |
| 2 | 自動セットアップ実行 | 5分 |
| 3 | .env編集 | 2分 |
| 4 | テスト投稿 | 1分 |
| 5 | スケジューラー起動 | 1分 |
| **合計** | | **10分** |

---

## 🎯 自動セットアップで実行されること

✅ Python仮想環境の作成
✅ 必要なパッケージのインストール
✅ Playwrightブラウザのインストール
✅ 環境変数ファイルの作成
✅ 動作テストの実行

**すべて自動です！**

---

## 💡 よくある質問

### Q1: Pythonがインストールされていない
**A**: 以下からインストールしてください
- Windows: https://www.python.org/downloads/
- Mac: `brew install python@3.11`
- Ubuntu: `sudo apt install python3.11`

### Q2: "setup.bat" がエラーになる
**A**: 管理者権限で実行してください
- setup.batを右クリック → "管理者として実行"

### Q3: Playwrightのインストールが失敗する
**A**: 手動でインストール
```bash
venv/bin/activate  # Windowsの場合: venv\Scripts\activate
playwright install chromium
```

### Q4: テスト投稿が失敗する
**A**: .envファイルの設定を確認
- APIキーが正しいか
- noteのメール・パスワードが正しいか
- `NOTE_USER_URLNAME=poker_jp` になっているか

### Q5: 毎日自動投稿したい
**A**: 以下のいずれかを選択

**方法A**: スケジューラースクリプト（PCを起動したまま）
```bash
./start_scheduler.sh  # Mac/Linux
start_scheduler.bat   # Windows
```

**方法B**: システムスケジューラー（PC再起動後も自動実行）

**Windows タスクスケジューラー**:
1. Windowsキー → "タスク スケジューラ"
2. タスクの作成
3. トリガー: 毎日 09:00
4. 操作: `C:\...\venv\Scripts\python.exe main.py post-real`

**Mac/Linux cron**:
```bash
crontab -e
# 以下を追加
0 9 * * * cd ~/ai-company/dev/poker-note-generator && source venv/bin/activate && python main.py post-real >> logs/cron.log 2>&1
```

---

## 🆘 トラブルシューティング

### エラー: "ANTHROPIC_API_KEY is required"
→ .envファイルのAPIキーを設定してください

### エラー: "Login failed"
→ noteのメールアドレス・パスワードを確認してください

### エラー: "playwright install failed"
→ ネット接続を確認してください

### 記事は生成されるが投稿されない
→ ログを確認: `cat logs/scheduler.log`

---

## 📞 サポート

問題が解決しない場合:
1. `logs/`ディレクトリのログファイルを確認
2. GitHubでIssueを作成
3. エラーメッセージをコピーして報告

---

## 🎉 完成！

セットアップが完了したら:

✅ 毎日午前9時に自動で記事生成
✅ noteに自動投稿（手動操作ゼロ）
✅ 週7記事を完全放置

**完全自動化システムの稼働開始です！** 🚀
