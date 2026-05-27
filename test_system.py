#!/usr/bin/env python3
"""
システム動作確認テストスクリプト
各モジュールが正しく動作するかチェック
"""
import os
import sys
from datetime import datetime

# カラー出力
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_header(msg):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{msg}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")


def test_imports():
    """依存パッケージのインポートテスト"""
    print_header("依存パッケージチェック")

    packages = [
        'anthropic',
        'requests',
        'bs4',
        'schedule',
        'dotenv',
        'pytrends'
    ]

    all_ok = True
    for package in packages:
        try:
            __import__(package)
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - インストールが必要です")
            all_ok = False

    return all_ok


def test_environment():
    """環境変数のチェック"""
    print_header("環境変数チェック")

    from dotenv import load_dotenv
    load_dotenv()

    # 必須
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print_success(f"ANTHROPIC_API_KEY: 設定済み ({api_key[:10]}...)")
    else:
        print_error("ANTHROPIC_API_KEY: 未設定")
        return False

    # オプション
    wp_url = os.getenv('WORDPRESS_URL')
    if wp_url:
        print_success(f"WORDPRESS_URL: {wp_url}")
    else:
        print_warning("WORDPRESS_URL: 未設定（ローカル保存のみ）")

    return True


def test_research_module():
    """Research部門のモジュールテスト"""
    print_header("Research部門テスト")

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'research'))

        # TrendCollector
        from research.trend_collector import TrendCollector
        collector = TrendCollector()
        print_success("TrendCollector初期化")

        # KeywordAnalyzer
        from research.keyword_analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        print_success("KeywordAnalyzer初期化")

        # サンプルデータでテスト
        sample_trends = [
            {'keyword': 'テストキーワード', 'source': 'test', 'timestamp': datetime.now().isoformat()}
        ]
        analyzed = analyzer.analyze_trends(sample_trends)
        if analyzed:
            print_success(f"キーワード分析: スコア={analyzed[0].get('affiliate_score', 0)}")

        return True

    except Exception as e:
        print_error(f"Research部門エラー: {e}")
        return False


def test_dev_module():
    """Dev部門のモジュールテスト"""
    print_header("Dev部門テスト")

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'dev'))

        # ArticleGenerator
        from dev.article_generator import ArticleGenerator
        generator = ArticleGenerator()
        print_success("ArticleGenerator初期化")

        # WordPressPublisher（オプション）
        wp_url = os.getenv('WORDPRESS_URL')
        if wp_url:
            from dev.wordpress_publisher import WordPressPublisher
            publisher = WordPressPublisher()
            if publisher.test_connection():
                print_success("WordPress接続: OK")
            else:
                print_warning("WordPress接続: 失敗")
        else:
            print_warning("WordPressPublisher: スキップ（WORDPRESS_URL未設定）")

        return True

    except Exception as e:
        print_error(f"Dev部門エラー: {e}")
        return False


def test_marketing_module():
    """Marketing部門のモジュールテスト"""
    print_header("Marketing部門テスト")

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'marketing'))

        # ContentScheduler
        from marketing.content_scheduler import ContentScheduler
        scheduler = ContentScheduler()
        print_success("ContentScheduler初期化")

        summary = scheduler.get_schedule_summary()
        print_success(f"スケジュール: {summary['total']}件登録済み")

        # PerformanceAnalyzer
        from marketing.content_scheduler import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer()
        print_success("PerformanceAnalyzer初期化")

        return True

    except Exception as e:
        print_error(f"Marketing部門エラー: {e}")
        return False


def test_pm_module():
    """PM部門のモジュールテスト"""
    print_header("PM部門テスト")

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'pm'))

        # AutomationOrchestrator
        from pm.automation_orchestrator import AutomationOrchestrator
        orchestrator = AutomationOrchestrator()
        print_success("AutomationOrchestrator初期化")

        status = orchestrator.get_system_status()
        print_success(f"システムステータス: {status['status']}")
        print_success(f"自動投稿: {'有効' if status['config']['auto_post_enabled'] else '無効'}")

        return True

    except Exception as e:
        print_error(f"PM部門エラー: {e}")
        return False


def test_directory_structure():
    """ディレクトリ構造のチェック"""
    print_header("ディレクトリ構造チェック")

    dirs = [
        'research',
        'research/data',
        'dev',
        'dev/articles',
        'dev/publish_logs',
        'marketing',
        'marketing/schedules',
        'marketing/analytics',
        'pm',
        'pm/logs'
    ]

    all_ok = True
    for dir_path in dirs:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        if os.path.isdir(full_path):
            print_success(f"{dir_path}/")
        else:
            print_error(f"{dir_path}/ - 存在しません")
            all_ok = False

    return all_ok


def main():
    """全テスト実行"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("AIアフィリエイト記事自動生成システム - 動作確認テスト")
    print(f"{'='*60}{Colors.END}\n")

    results = []

    # 各テスト実行
    results.append(("依存パッケージ", test_imports()))
    results.append(("環境変数", test_environment()))
    results.append(("ディレクトリ構造", test_directory_structure()))
    results.append(("Research部門", test_research_module()))
    results.append(("Dev部門", test_dev_module()))
    results.append(("Marketing部門", test_marketing_module()))
    results.append(("PM部門", test_pm_module()))

    # 結果サマリー
    print_header("テスト結果サマリー")

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        if ok:
            print_success(f"{name}: 合格")
        else:
            print_error(f"{name}: 失敗")

    print(f"\n{'='*60}")
    if passed == total:
        print(f"{Colors.GREEN}✓ すべてのテストに合格しました！ ({passed}/{total}){Colors.END}")
        print(f"\n🚀 システムは正常に動作します")
        print(f"\n次のステップ:")
        print(f"  python run_automation.py --mode once --skip-publish --max-articles 1")
    else:
        print(f"{Colors.RED}✗ {total - passed}個のテストが失敗しました ({passed}/{total}){Colors.END}")
        print(f"\n修正が必要な項目を確認してください")

    print(f"{'='*60}\n")

    return passed == total


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}テストを中断しました{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}予期しないエラー: {e}{Colors.END}\n")
        sys.exit(1)
