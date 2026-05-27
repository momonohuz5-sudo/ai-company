# ポーカー戦略note自動投稿システム - 完全自動化セットアップガイド

## 🚀 このガイドで実現できること

- ✅ **毎日自動で記事生成**
- ✅ **noteに自動投稿**（手動操作ゼロ）
- ✅ **スケジューラーで完全自動化**（朝9時に自動投稿）
- ✅ **週7記事を完全放置**

所要時間: **約15分**

---

## 📋 必要なもの

### 1. PCスペック
- Windows 10/11、Mac、またはLinux
- CPU: 2コア以上
- メモリ: 2GB以上
- 空き容量: 1GB以上

### 2. 必要なアカウント
- ✅ noteアカウント（既にお持ち: poker_jp）
- ✅ Anthropic API キー（既に取得済み）

### 3. 必要な情報（既に準備済み）
- note メール: momonohuz5@gmail.com
- note パスワード: momonohuZ5
- note ユーザーID: poker_jp
- Anthropic API キー: sk-ant-api03-...

---

## 🔧 セットアップ手順

### ステップ1: リポジトリをクローン（5分）

#### Windows
1. **Git for Windowsをインストール**（未インストールの場合）
   - https://git-scm.com/download/win からダウンロード
   - インストール後、コマンドプロンプトを開く

2. **リポジトリをクローン**
```cmd
cd C:\
git clone https://github.com/momonohuz5-sudo/ai-company.git
cd ai-company\dev\poker-note-generator
```

#### Mac
1. **ターミナルを開く**（Command + Space → "Terminal"）

2. **リポジトリをクローン**
```bash
cd ~
git clone https://github.com/momonohuz5-sudo/ai-company.git
cd ai-company/dev/poker-note-generator
```

#### Linux
```bash
cd ~
git clone https://github.com/momonohuz5-sudo/ai-company.git
cd ai-company/dev/poker-note-generator
```

---

### ステップ2: Python環境のセットアップ（5分）

#### Windows

1. **Python 3.11をインストール**（未インストールの場合）
   - https://www.python.org/downloads/ からダウンロード
   - インストール時に「Add Python to PATH」にチェック

2. **仮想環境を作成**
```cmd
python -m venv venv
venv\Scripts\activate
```

3. **依存パッケージをインストール**
```cmd
pip install anthropic python-dotenv matplotlib numpy apscheduler playwright
pip install NoteClient2
playwright install chromium
```

#### Mac / Linux

1. **Python 3.11をインストール**（未インストールの場合）
```bash
# Mac (Homebrewを使用)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv
```

2. **仮想環境を作成**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

3. **依存パッケージをインストール**
```bash
pip install anthropic python-dotenv matplotlib numpy apscheduler playwright
pip install NoteClient2
playwright install chromium
```

---

### ステップ3: 環境変数の設定（2分）

`.env`ファイルは既に設定済みですが、確認しましょう。

```bash
# Windows
notepad .env

# Mac/Linux
nano .env
```

以下の内容になっているか確認：

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# note認証情報
NOTE_EMAIL=momonohuz5@gmail.com
NOTE_PASSWORD=momonohuZ5
NOTE_USER_URLNAME=poker_jp

# マガジン設定（後で設定可能）
NOTE_MAGAZINE_ID=
NOTE_ARTICLE_PRICE=0

# スケジューリング
PUBLISH_TIME=09:00
TIMEZONE=Asia/Tokyo

# ログ設定
LOG_LEVEL=INFO
```

**重要**: `NOTE_ARTICLE_PRICE=0`（無料記事）になっていることを確認

---

### ステップ4: 動作テスト（3分）

#### テスト1: 記事生成テスト
```bash
python main.py test-content
```

**期待される出力**:
```
=== ポーカー戦略記事生成テスト ===
✓ 設定OK
✓ ContentGenerator初期化OK
記事生成中...
✓ 記事生成完了
タイトル: ...
文字数: 2000字以上
```

#### テスト2: 自動投稿テスト（実際に投稿されます！）
```bash
python main.py post-real
```

**期待される出力**:
```
=== note実投稿モード ===
⚠️  実際にnote.comへ投稿します...
✓ 投稿完了！
タイトル: ...
note URL: https://note.com/poker_jp/n/...
```

**✅ ここまで成功したら、自動投稿システムは動作しています！**

note.com/poker_jpにアクセスして、記事が投稿されているか確認してください。

---

## 🤖 完全自動化：スケジューラー起動

### 方法A: 組み込みスケジューラー（推奨）

毎日午前9時に自動投稿します。

#### Windows
```cmd
# run_scheduler.bat を作成
@echo off
cd C:\ai-company\dev\poker-note-generator
venv\Scripts\activate
python -c "from src.scheduler import ArticleScheduler; scheduler = ArticleScheduler(); scheduler.start()"
```

実行:
```cmd
run_scheduler.bat
```

**PCを起動したままにしておく必要があります**

#### Mac/Linux
```bash
# run_scheduler.sh を作成
#!/bin/bash
cd ~/ai-company/dev/poker-note-generator
source venv/bin/activate
python -c "from src.scheduler import ArticleScheduler; scheduler = ArticleScheduler(); scheduler.start()"
```

実行:
```bash
chmod +x run_scheduler.sh
./run_scheduler.sh
```

---

### 方法B: システムタスクスケジューラー（完全自動）

PCを再起動しても自動で実行されます。

#### Windows タスクスケジューラー

1. **タスクスケジューラーを開く**
   - Windowsキー → "タスク スケジューラ" と入力

2. **新しいタスクを作成**
   - 「タスクの作成」をクリック
   - 名前: "ポーカーnote自動投稿"

3. **トリガー設定**
   - 「トリガー」タブ → 「新規」
   - 開始: 毎日 09:00
   - 繰り返し間隔: 1日

4. **操作設定**
   - 「操作」タブ → 「新規」
   - プログラム: `C:\ai-company\dev\poker-note-generator\venv\Scripts\python.exe`
   - 引数: `main.py post-real`
   - 開始: `C:\ai-company\dev\poker-note-generator`

5. **条件設定**
   - 「条件」タブ
   - ✅ コンピューターをAC電源で使用している場合のみ実行する（オフ）
   - ✅ スリープ解除して実行する（オン）

**完了！** 毎日9時に自動投稿されます。

#### Mac cron

1. **crontabを編集**
```bash
crontab -e
```

2. **以下を追加**
```bash
0 9 * * * cd ~/ai-company/dev/poker-note-generator && source venv/bin/activate && python main.py post-real >> logs/cron.log 2>&1
```

3. **保存して終了**

**完了！** 毎日9時に自動投稿されます。

#### Linux systemd

1. **サービスファイルを作成**
```bash
sudo nano /etc/systemd/system/poker-note.service
```

2. **以下を記述**
```ini
[Unit]
Description=Poker Note Auto Publisher
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/ai-company/dev/poker-note-generator
ExecStart=/home/youruser/ai-company/dev/poker-note-generator/venv/bin/python main.py post-real
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

3. **タイマーファイルを作成**
```bash
sudo nano /etc/systemd/system/poker-note.timer
```

```ini
[Unit]
Description=Poker Note Daily Timer

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

4. **有効化**
```bash
sudo systemctl enable poker-note.timer
sudo systemctl start poker-note.timer
```

**完了！** 毎日9時に自動投稿されます。

---

## 🎯 動作確認

### 1. 今すぐ投稿してテスト
```bash
python main.py post-real
```

### 2. note.comで確認
https://note.com/poker_jp にアクセスして、記事が投稿されているか確認

### 3. スケジューラーのログ確認
```bash
# ログディレクトリを確認
ls logs/

# 最新のログを表示
cat logs/scheduler.log
```

---

## 📊 運用パターン

### パターンA: 毎日1記事（推奨）
- 朝9時に自動投稿
- 週7記事
- 読者が飽きない頻度

**設定**: そのままでOK

### パターンB: 週3記事
- 月・水・金の朝9時
- ゆっくりペース

**設定**: `src/scheduler.py`を編集
```python
# 月水金のみ投稿
if datetime.now().weekday() in [0, 2, 4]:  # 月=0, 水=2, 金=4
    # 投稿処理
```

### パターンC: 1日2記事
- 朝9時と夜21時
- 高頻度投稿

**設定**: スケジューラーを2つ起動

---

## ⚠️ トラブルシューティング

### エラー1: "playwright install chromium"が失敗
```bash
# 手動でインストール
python -m playwright install chromium
python -m playwright install-deps chromium
```

### エラー2: "NoteClient2"が見つからない
```bash
pip install NoteClient2 --upgrade
```

### エラー3: 投稿が失敗する
- noteのログイン情報を確認
- パスワードに特殊文字が含まれている場合、`""`で囲む
```env
NOTE_PASSWORD="momonohuZ5"
```

### エラー4: 記事は生成されるが投稿されない
```bash
# ログを確認
cat logs/scheduler.log

# Playwrightの動作確認
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(headless=False); print('OK'); browser.close()"
```

---

## 🎉 完全自動化完了！

これで以下が実現されました：

✅ **毎日午前9時に自動で記事生成**
✅ **noteに自動投稿**（手動操作ゼロ）
✅ **PCを起動したままor再起動後も自動実行**
✅ **週7記事を完全放置**

### 次のステップ

1. **1週間様子を見る**
   - 記事の品質確認
   - 読者の反応確認

2. **マガジン作成**（収益化）
   - noteプレミアム登録（¥500/月）
   - 定期購読マガジン作成（¥500/月）
   - 有料記事の投稿開始

3. **記事の最適化**
   - 読者のフィードバックを元に改善
   - トピックの追加・変更

---

## 💰 収益化シミュレーション

### 1ヶ月後
- 無料記事: 30本
- 読者: 50-100人
- 収益: ¥0（認知拡大期）

### 3ヶ月後
- 記事累計: 90本
- 読者: 200-500人
- マガジン購読者: 10-20人
- **月額収益: ¥5,000-10,000**

### 6ヶ月後
- 記事累計: 180本
- 読者: 500-1,000人
- マガジン購読者: 30-50人
- **月額収益: ¥15,000-25,000**

**コスト**:
- Claude API: ¥3,000-5,000/月
- noteプレミアム: ¥500/月
- 電気代: ¥300/月
- **合計**: 約¥4,000-6,000/月

**純利益**: ¥10,000-20,000/月（3-6ヶ月後）

---

## 📞 サポート

問題が発生した場合：
1. `logs/`ディレクトリのログを確認
2. GitHubでIssueを作成
3. このガイドのトラブルシューティングを確認

---

**セットアップ完了！自動化システムが稼働を開始します** 🚀

手順通りに進めれば、15分で完全自動化が実現します。
頑張ってください！
