@echo off
REM ポーカー戦略note自動投稿システム - 自動セットアップスクリプト (Windows)
REM 使い方: setup.bat をダブルクリック

setlocal enabledelayedexpansion

echo ======================================
echo   ポーカーnote自動投稿システム
echo   自動セットアップ開始
echo ======================================
echo.

REM カレントディレクトリを設定
cd /d "%~dp0"

echo 📍 作業ディレクトリ: %CD%
echo.

REM ステップ1: Pythonバージョン確認
echo 🔍 ステップ1/6: Pythonバージョン確認
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pythonがインストールされていません
    echo.
    echo インストール方法:
    echo   https://www.python.org/downloads/ からダウンロード
    echo   インストール時に "Add Python to PATH" にチェック
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python確認完了: %PYTHON_VERSION%
echo.

REM ステップ2: 仮想環境作成
echo 🔧 ステップ2/6: 仮想環境作成
if exist venv (
    echo ⚠ 既存の仮想環境を削除して再作成します
    rmdir /s /q venv
)

python -m venv venv
call venv\Scripts\activate.bat

echo ✓ 仮想環境作成完了
echo.

REM ステップ3: 依存パッケージインストール
echo 📦 ステップ3/6: 依存パッケージインストール
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo ✓ パッケージインストール完了
echo.

REM ステップ4: Playwrightブラウザインストール
echo 🌐 ステップ4/6: Playwrightブラウザインストール
playwright install chromium

echo ✓ Chromiumインストール完了
echo.

REM ステップ5: 環境変数確認
echo ⚙️  ステップ5/6: 環境変数確認
if not exist .env (
    echo ⚠ .envファイルが見つかりません
    echo テンプレートを作成します...
    (
        echo # Claude API
        echo ANTHROPIC_API_KEY=your-api-key-here
        echo.
        echo # note認証情報
        echo NOTE_EMAIL=your-email@example.com
        echo NOTE_PASSWORD=your-password
        echo NOTE_USER_URLNAME=your-user-id
        echo.
        echo # マガジン設定
        echo NOTE_MAGAZINE_ID=
        echo NOTE_ARTICLE_PRICE=0
        echo.
        echo # スケジューリング
        echo PUBLISH_TIME=09:00
        echo TIMEZONE=Asia/Tokyo
        echo.
        echo # ログ設定
        echo LOG_LEVEL=INFO
    ) > .env
    echo ⚠ .envファイルを編集して、APIキーとnote認証情報を設定してください
    echo 編集: notepad .env
) else (
    echo ✓ .envファイル存在確認
)
echo.

REM ステップ6: 動作テスト
echo 🧪 ステップ6/6: 動作テスト
echo 記事生成テストを実行します...

python main.py test-content > test_output.txt 2>&1
findstr /C:"✓ 記事生成完了" test_output.txt >nul
if errorlevel 1 (
    echo ⚠ 記事生成テストに失敗しました
    echo   .envファイルのANTHROPIC_API_KEYを確認してください
) else (
    echo ✓ 記事生成テスト成功！
)
del test_output.txt
echo.

REM セットアップ完了
echo ======================================
echo ✅ セットアップ完了！
echo ======================================
echo.

REM 次のステップを表示
echo 📝 次のステップ:
echo.
echo 1. .envファイルを編集（まだの場合）:
echo    notepad .env
echo.
echo 2. テスト投稿を実行:
echo    venv\Scripts\activate
echo    python main.py post-real
echo.
echo 3. 自動投稿を確認後、タスクスケジューラーで毎日9時に自動実行:
echo    - Windowsキー → "タスク スケジューラ"
echo    - タスクの作成
echo    - トリガー: 毎日 9:00
echo    - 操作: プログラム %CD%\venv\Scripts\python.exe
echo    - 引数: main.py post-real
echo    - 開始: %CD%
echo.
echo 🎉 完全自動化の準備が整いました！
echo.
pause
