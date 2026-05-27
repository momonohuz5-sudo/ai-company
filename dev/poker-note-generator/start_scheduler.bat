@echo off
REM スケジューラー起動スクリプト (Windows)

cd /d "%~dp0"

echo ======================================
echo   ポーカーnote自動投稿スケジューラー
echo ======================================
echo.
echo 毎日午前9時に自動投稿を実行します
echo 停止: Ctrl+C
echo.

REM 仮想環境をアクティベート
call venv\Scripts\activate.bat

REM スケジューラー起動
python -c "from src.scheduler import ArticleScheduler; print('✓ スケジューラー起動'); print('✓ 次回実行: 明日 午前9時'); print(''); scheduler = ArticleScheduler(); scheduler.start()"
