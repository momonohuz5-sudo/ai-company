#!/usr/bin/env python3
"""
AIアフィリエイト記事自動生成システム - メイン実行スクリプト

使い方:
  # 1回のみ実行（テスト用）
  python run_automation.py --mode once

  # 24時間自動運用
  python run_automation.py --mode daemon

  # 記事生成のみ（投稿なし）
  python run_automation.py --mode once --skip-publish
"""
import os
import sys
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), 'pm'))

from pm.automation_orchestrator import AutomationOrchestrator


def check_environment():
    """環境変数の確認"""
    required_vars = ['ANTHROPIC_API_KEY']
    optional_vars = ['WORDPRESS_URL', 'WORDPRESS_USERNAME', 'WORDPRESS_APP_PASSWORD']

    print("="*60)
    print("環境変数チェック")
    print("="*60)

    all_ok = True

    print("\n【必須】")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: 設定済み")
        else:
            print(f"✗ {var}: 未設定")
            all_ok = False

    print("\n【オプション】")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: 設定済み")
        else:
            print(f"- {var}: 未設定（ローカル保存のみ）")

    print("\n" + "="*60)

    if not all_ok:
        print("\n⚠️  必須の環境変数が不足しています")
        print("📝 .env ファイルを作成して設定してください\n")
        sys.exit(1)

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='AIアフィリエイト記事自動生成システム',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 1回実行（テスト）
  python run_automation.py --mode once

  # 24時間自動運用
  python run_automation.py --mode daemon

  # 記事生成のみ
  python run_automation.py --mode once --skip-publish

  # 最大3件の記事を生成
  python run_automation.py --mode once --max-articles 3
        """
    )

    parser.add_argument(
        '--mode',
        choices=['once', 'daemon'],
        default='once',
        help='実行モード (once: 1回のみ, daemon: 24時間自動運用)'
    )

    parser.add_argument(
        '--skip-publish',
        action='store_true',
        help='投稿をスキップ（記事生成のみ）'
    )

    parser.add_argument(
        '--max-articles',
        type=int,
        help='最大記事生成数（デフォルト: 環境変数 MAX_ARTICLES_PER_DAY）'
    )

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='環境変数チェックのみ実行'
    )

    args = parser.parse_args()

    # 環境変数チェック
    check_environment()

    if args.check_only:
        print("\n✓ 環境設定OK")
        return

    # オーケストレーター初期化
    config = {}
    if args.max_articles:
        config['max_articles_per_day'] = args.max_articles

    orchestrator = AutomationOrchestrator(config=config if config else None)

    # 実行モードに応じて処理
    if args.mode == 'daemon':
        print("\n🤖 24時間自動運用モードで起動します...\n")
        orchestrator.start_scheduler()
    else:
        print("\n🚀 1回実行モードで起動します...\n")
        if args.skip_publish:
            # 記事生成まで
            keywords = orchestrator.run_trend_collection_pipeline()
            if keywords:
                orchestrator.run_article_generation_pipeline(keywords)
        else:
            # フルサイクル実行
            orchestrator.run_full_automation_cycle()

        print("\n✓ 処理完了\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 システムを停止しました\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ エラー: {e}\n")
        sys.exit(1)
