#!/bin/bash
# スケジューラー起動スクリプト (Mac/Linux)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================"
echo "  ポーカーnote自動投稿スケジューラー"
echo "======================================"
echo ""
echo "毎日午前9時に自動投稿を実行します"
echo "停止: Ctrl+C"
echo ""

# 仮想環境をアクティベート
source venv/bin/activate

# スケジューラー起動
python -c "
from src.scheduler import ArticleScheduler
import signal
import sys

def signal_handler(sig, frame):
    print('\n\nスケジューラーを停止します...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print('✓ スケジューラー起動')
print('✓ 次回実行: 明日 午前9時')
print('')

scheduler = ArticleScheduler()
scheduler.start()
"
