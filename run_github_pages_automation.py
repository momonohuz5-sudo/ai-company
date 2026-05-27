#!/usr/bin/env python3
"""
GitHub Pages アフィリエイト自動化システム - メイン実行スクリプト

トレンド収集 → 記事生成 → 投稿まで自動実行
"""

import os
import sys
import argparse
from datetime import datetime
import time

# 各部門のモジュールをインポート
sys.path.append(os.path.dirname(__file__))
from research.trend_collector import TrendCollector
from dev.article_generator_github import ArticleGenerator
from marketing.github_pages_publisher import GitHubPagesPublisher


class AutomationOrchestrator:
    """自動化オーケストレーター"""

    def __init__(self, skip_publish: bool = False):
        """
        初期化

        Args:
            skip_publish: Trueの場合、実際の投稿はスキップ（テスト用）
        """
        self.trend_collector = TrendCollector()
        self.article_generator = ArticleGenerator()
        self.publisher = GitHubPagesPublisher()
        self.skip_publish = skip_publish

    def run_once(self, max_articles: int = 3, category: str = "all"):
        """
        1回だけ実行（トレンド収集 → 記事生成 → 投稿）

        Args:
            max_articles: 生成する記事数
            category: カテゴリー
        """

        print(f"\n{'='*60}")
        print(f"🚀 GitHub Pages アフィリエイト自動化システム 実行開始")
        print(f"{'='*60}\n")

        print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 最大記事数: {max_articles}")
        print(f"📁 カテゴリー: {category}")
        print(f"🔍 テストモード: {'有効' if self.skip_publish else '無効'}\n")

        # ステップ1: トレンド収集
        print("\n" + "="*60)
        print("📈 ステップ1: トレンド情報収集")
        print("="*60)

        trends = self.trend_collector.collect_trends(
            category=category,
            limit=max_articles
        )

        print(f"✅ {len(trends)}件のトレンドを収集しました\n")
        for i, trend in enumerate(trends, 1):
            print(f"{i}. {trend['keyword']} (スコア: {trend['score']})")

        # ステップ2: 記事生成 & 投稿
        print("\n" + "="*60)
        print("✍️  ステップ2: 記事生成 & 投稿")
        print("="*60 + "\n")

        generated_count = 0
        for i, trend in enumerate(trends, 1):
            print(f"\n--- 記事 {i}/{len(trends)} ---")
            print(f"トピック: {trend['keyword']}")

            try:
                # 記事生成
                print("  ⏳ 記事生成中...")
                article = self.article_generator.generate_article(
                    topic=trend["keyword"],
                    keywords=[trend["keyword"]] + [trend["category"]],
                    category=trend["category"],
                    target_length=2000
                )

                print(f"  ✅ 記事生成完了: {article['title']}")

                # 投稿
                print("  ⏳ 投稿中...")
                filepath = self.publisher.publish_article(
                    article=article,
                    categories=[trend["category"]],
                    skip_publish=self.skip_publish
                )

                print(f"  ✅ 投稿完了: {os.path.basename(filepath)}")

                generated_count += 1

            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue

        # 完了サマリー
        print("\n" + "="*60)
        print("🎉 実行完了")
        print("="*60)
        print(f"✅ 生成記事数: {generated_count}/{len(trends)}")

        if not self.skip_publish:
            print("\n📢 次のステップ:")
            print("  1. git add docs/_posts/")
            print("  2. git commit -m 'Add new articles'")
            print("  3. git push")
            print("\n  プッシュ後、GitHub Pagesに自動デプロイされます！")
        else:
            print("\n🔍 テストモードで実行しました（実際の投稿なし）")

        print()

    def run_daemon(self, interval_hours: int = 8, articles_per_run: int = 3):
        """
        デーモンモード（定期実行）

        Args:
            interval_hours: 実行間隔（時間）
            articles_per_run: 1回あたりの記事数
        """

        print(f"\n{'='*60}")
        print(f"🔄 デーモンモード起動")
        print(f"{'='*60}\n")
        print(f"⏰ 実行間隔: {interval_hours}時間")
        print(f"📊 1回あたりの記事数: {articles_per_run}")
        print(f"\n実行を停止するには Ctrl+C を押してください\n")

        run_count = 0
        while True:
            run_count += 1
            print(f"\n{'='*60}")
            print(f"🔄 実行回数: {run_count}")
            print(f"{'='*60}")

            try:
                self.run_once(max_articles=articles_per_run, category="all")
            except Exception as e:
                print(f"❌ エラーが発生しました: {e}")

            # 次回実行まで待機
            next_run = datetime.now().timestamp() + (interval_hours * 3600)
            next_run_str = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')

            print(f"\n⏰ 次回実行: {next_run_str}")
            print(f"💤 {interval_hours}時間待機中...\n")

            time.sleep(interval_hours * 3600)


def main():
    """メイン関数"""

    parser = argparse.ArgumentParser(
        description="GitHub Pages アフィリエイト自動化システム"
    )

    parser.add_argument(
        "--mode",
        choices=["once", "daemon"],
        default="once",
        help="実行モード: once=1回のみ, daemon=定期実行"
    )

    parser.add_argument(
        "--max-articles",
        type=int,
        default=3,
        help="生成する記事数（onceモード）"
    )

    parser.add_argument(
        "--category",
        default="all",
        help="カテゴリー: all, AI, tech, books, etc."
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=8,
        help="実行間隔（時間、daemonモード）"
    )

    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="投稿をスキップ（テストモード）"
    )

    args = parser.parse_args()

    # ANTHROPIC_API_KEY チェック
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ エラー: ANTHROPIC_API_KEY 環境変数が設定されていません")
        print("\n設定方法:")
        print("  export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    # オーケストレーター初期化
    orchestrator = AutomationOrchestrator(skip_publish=args.skip_publish)

    # 実行
    if args.mode == "once":
        orchestrator.run_once(
            max_articles=args.max_articles,
            category=args.category
        )
    else:
        orchestrator.run_daemon(
            interval_hours=args.interval,
            articles_per_run=args.max_articles
        )


if __name__ == "__main__":
    main()
