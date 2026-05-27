#!/bin/bash
# ポーカー記事自動投稿スケジューラー起動スクリプト

cd "$(dirname "$0")"

# 仮想環境があればアクティベート
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# ログディレクトリ作成
mkdir -p logs

# スケジューラー起動
echo "Starting poker article scheduler..."
echo "Logs: logs/scheduler_$(date +%Y%m%d).log"

python -m src.scheduler "$@" 2>&1 | tee "logs/scheduler_$(date +%Y%m%d).log"
