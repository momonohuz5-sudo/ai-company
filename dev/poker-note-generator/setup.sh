#!/bin/bash
# ポーカー戦略note自動投稿システム - 自動セットアップスクリプト (Mac/Linux)
# 使い方: bash setup.sh

set -e  # エラーで停止

echo "======================================"
echo "  ポーカーnote自動投稿システム"
echo "  自動セットアップ開始"
echo "======================================"
echo ""

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 現在のディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📍 作業ディレクトリ: $SCRIPT_DIR"
echo ""

# ステップ1: Pythonバージョン確認
echo "🔍 ステップ1/6: Pythonバージョン確認"
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$PYTHON_VERSION" == "3.11" ]] || [[ "$PYTHON_VERSION" == "3.12" ]]; then
        PYTHON_CMD=python3
    else
        echo -e "${RED}❌ Python 3.11以上が必要です${NC}"
        echo "インストール方法:"
        echo "  Mac: brew install python@3.11"
        echo "  Ubuntu: sudo apt install python3.11"
        exit 1
    fi
else
    echo -e "${RED}❌ Pythonがインストールされていません${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python確認完了: $($PYTHON_CMD --version)${NC}"
echo ""

# ステップ2: 仮想環境作成
echo "🔧 ステップ2/6: 仮想環境作成"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ 既存の仮想環境を削除して再作成します${NC}"
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
source venv/bin/activate

echo -e "${GREEN}✓ 仮想環境作成完了${NC}"
echo ""

# ステップ3: 依存パッケージインストール
echo "📦 ステップ3/6: 依存パッケージインストール"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo -e "${GREEN}✓ パッケージインストール完了${NC}"
echo ""

# ステップ4: Playwrightブラウザインストール
echo "🌐 ステップ4/6: Playwrightブラウザインストール"
playwright install chromium
# システム依存関係は失敗しても続行
playwright install-deps chromium 2>/dev/null || echo -e "${YELLOW}⚠ システム依存関係のインストールをスキップ${NC}"

echo -e "${GREEN}✓ Chromiumインストール完了${NC}"
echo ""

# ステップ5: 環境変数確認
echo "⚙️  ステップ5/6: 環境変数確認"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .envファイルが見つかりません${NC}"
    echo "テンプレートを作成します..."
    cat > .env << 'EOF'
# Claude API
ANTHROPIC_API_KEY=your-api-key-here

# note認証情報
NOTE_EMAIL=your-email@example.com
NOTE_PASSWORD=your-password
NOTE_USER_URLNAME=your-user-id

# マガジン設定
NOTE_MAGAZINE_ID=
NOTE_ARTICLE_PRICE=0

# スケジューリング
PUBLISH_TIME=09:00
TIMEZONE=Asia/Tokyo

# ログ設定
LOG_LEVEL=INFO
EOF
    echo -e "${YELLOW}⚠ .envファイルを編集して、APIキーとnote認証情報を設定してください${NC}"
    echo "編集: nano .env"
else
    echo -e "${GREEN}✓ .envファイル存在確認${NC}"
fi
echo ""

# ステップ6: 動作テスト
echo "🧪 ステップ6/6: 動作テスト"
echo "記事生成テストを実行します..."

if python main.py test-content 2>&1 | grep -q "✓ 記事生成完了"; then
    echo -e "${GREEN}✓ 記事生成テスト成功！${NC}"
else
    echo -e "${YELLOW}⚠ 記事生成テストに失敗しました${NC}"
    echo "  .envファイルのANTHROPIC_API_KEYを確認してください"
fi
echo ""

# セットアップ完了
echo "======================================"
echo -e "${GREEN}✅ セットアップ完了！${NC}"
echo "======================================"
echo ""

# 次のステップを表示
echo "📝 次のステップ:"
echo ""
echo "1. .envファイルを編集（まだの場合）:"
echo "   nano .env"
echo ""
echo "2. テスト投稿を実行:"
echo "   source venv/bin/activate"
echo "   python main.py post-real"
echo ""
echo "3. 自動投稿を確認後、スケジューラーを起動:"
echo "   ./start_scheduler.sh"
echo ""
echo "4. または、cronで毎日9時に自動実行:"
echo "   crontab -e"
echo "   以下を追加:"
echo "   0 9 * * * cd $SCRIPT_DIR && source venv/bin/activate && python main.py post-real >> logs/cron.log 2>&1"
echo ""
echo -e "${GREEN}🎉 完全自動化の準備が整いました！${NC}"
