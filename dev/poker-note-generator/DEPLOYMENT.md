# デプロイメントガイド

## 本番環境セットアップ

### 1. サーバー要件

- **OS**: Ubuntu 20.04+ / Debian 11+
- **Python**: 3.12.7
- **メモリ**: 最低2GB（4GB推奨）
- **ストレージ**: 10GB以上

### 2. 環境構築

```bash
# リポジトリクローン
git clone https://github.com/your-org/ai-company.git
cd ai-company/dev/poker-note-generator

# Python仮想環境作成
python3.12 -m venv venv
source venv/bin/activate

# 依存パッケージインストール
pip install -r requirements.txt

# Playwright（Note Client 2用）
playwright install
```

### 3. 環境変数設定

```bash
# .envファイル作成
cp .env.example .env
nano .env
```

必須の設定:

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# note認証情報
NOTE_EMAIL=your-email@example.com
NOTE_PASSWORD=your-password
NOTE_USER_URL_ID=your-user-id

# マガジンID（noteで作成後に設定）
NOTE_MAGAZINE_ID=12345

# 記事価格（円）
NOTE_ARTICLE_PRICE=500

# 投稿時刻
PUBLISH_TIME=09:00
TIMEZONE=Asia/Tokyo
```

### 4. noteマガジン準備

1. [note.com](https://note.com)でプレミアム会員登録（月額500円）
2. 定期購読マガジンを作成
3. マガジンIDを取得して`.env`に設定

### 5. テスト実行

```bash
# モックモードでワークフローテスト
python main.py test-workflow

# スケジューラーを1回だけ実行
python -m src.scheduler --mock --once
```

### 6. 本番起動

#### オプション1: フォアグラウンド実行

```bash
# モックモード（安全）
./run_scheduler.sh --mock

# 本番モード
./run_scheduler.sh
```

#### オプション2: systemdサービス化（推奨）

```bash
# サービスファイル作成
sudo nano /etc/systemd/system/poker-note-scheduler.service
```

内容:

```ini
[Unit]
Description=Poker Strategy Note Article Scheduler
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ai-company/dev/poker-note-generator
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python -m src.scheduler
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

有効化:

```bash
sudo systemctl daemon-reload
sudo systemctl enable poker-note-scheduler
sudo systemctl start poker-note-scheduler

# 状態確認
sudo systemctl status poker-note-scheduler

# ログ確認
sudo journalctl -u poker-note-scheduler -f
```

#### オプション3: tmuxセッション

```bash
# tmuxセッション作成
tmux new -s poker-scheduler

# スケジューラー起動
./run_scheduler.sh

# デタッチ: Ctrl+B → D
# 再接続: tmux attach -t poker-scheduler
```

## モニタリング

### ログ確認

```bash
# 最新ログ
tail -f logs/scheduler_$(date +%Y%m%d).log

# 過去のログ
ls -lh logs/
```

### 投稿状況確認

- noteマガジンページで投稿を確認
- `output/articles/` に生成済み記事のバックアップ
- `output/images/` にレンジチャート画像

## トラブルシューティング

### 投稿エラー

1. **note認証エラー**
   - `.env`の認証情報を確認
   - noteでログインできるか手動確認

2. **Claude API制限**
   - APIキーの利用状況を確認
   - レート制限に引っかかっている場合は待機

3. **Playwright エラー**
   - `playwright install` を再実行
   - ブラウザの依存パッケージを確認

### モックモードで安全確認

問題があれば、まずモックモードで動作確認:

```bash
python -m src.scheduler --mock --once
```

## バックアップ・復旧

### バックアップ対象

- `.env` ファイル（認証情報）
- `output/articles/` （生成記事）
- `database.db` （将来実装時）

### 復旧手順

```bash
# バックアップ
tar -czf backup_$(date +%Y%m%d).tar.gz .env output/ database.db

# 復元
tar -xzf backup_YYYYMMDD.tar.gz
```

## コスト管理

### 月額コスト見積もり

| 項目 | 月額 |
|------|------|
| Claude API | $30-100 |
| noteプレミアム | ¥500 |
| サーバー（VPS） | $0-50 |
| **合計** | **¥5,000-15,000** |

### コスト削減のヒント

- Prompt Cachingを活用（30-50%削減）
- 記事生成頻度を調整（週5本→週3本など）
- Raspberry Piなどで自宅運用

## セキュリティ

- ✅ `.env`ファイルは`.gitignore`に追加済み
- ✅ APIキーはサーバーのみに保管
- ⚠️ noteパスワードは強固なものを使用
- ⚠️ サーバーのSSHキー認証を推奨

## サポート

問題が発生した場合:

1. ログを確認
2. モックモードでテスト
3. GitHub Issuesで報告
