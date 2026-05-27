#!/usr/bin/env python3
"""
GitHub Pages自動アフィリエイトシステム - メイン実行スクリプト
トレンド収集 → 記事生成 → GitHub Pages投稿を自動化
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from dev.article_generator_github import GitHubPagesArticleGenerator
from marketing.github_pages_publisher import GitHubPagesPublisher

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_pages_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GitHubPagesAutomation:
    """GitHub Pages自動投稿オーケストレーター"""

    def __init__(self):
        """初期化"""
        self.generator = GitHubPagesArticleGenerator()
        self.publisher = GitHubPagesPublisher()

    def generate_and_publish_article(
        self,
        topic: str,
        keywords: list[str],
        categories: list[str] = None,
        tags: list[str] = None,
        affiliate_products: list[dict] = None
    ) -> dict:
        """
        記事生成から投稿までを実行

        Args:
            topic: トピック
            keywords: SEOキーワード
            categories: Jekyllカテゴリー
            tags: Jekyllタグ
            affiliate_products: アフィリエイト商品情報

        Returns:
            実行結果
        """
        logger.info(f"記事生成開始: {topic}")

        # 1. 記事生成
        article_result = self.generator.generate_article(
            topic=topic,
            keywords=keywords,
            target_length=2500,
            affiliate_products=affiliate_products
        )

        if not article_result["success"]:
            logger.error(f"記事生成失敗: {article_result.get('error')}")
            return article_result

        # 2. GitHub Pagesに投稿
        publish_result = self.publisher.publish_article(
            title=article_result["title"],
            content=article_result["content"],
            categories=categories or ["AI"],
            tags=tags or keywords,
            excerpt=article_result.get("excerpt")
        )

        if publish_result["success"]:
            logger.info(f"投稿成功: {publish_result['filepath']}")
        else:
            logger.error(f"投稿失敗: {publish_result.get('error')}")

        return {
            "success": publish_result["success"],
            "article": article_result,
            "publish": publish_result
        }

    def run_batch(self, articles_config: list[dict]) -> list[dict]:
        """
        複数記事の一括生成・投稿

        Args:
            articles_config: 記事設定のリスト

        Returns:
            実行結果のリスト
        """
        results = []

        for i, config in enumerate(articles_config, 1):
            logger.info(f"記事 {i}/{len(articles_config)} を処理中...")

            result = self.generate_and_publish_article(**config)
            results.append(result)

            # API制限対策（次の記事まで少し待機）
            if i < len(articles_config):
                time.sleep(2)

        return results


def get_sample_articles() -> list[dict]:
    """サンプル記事設定を取得"""
    return [
        {
            "topic": "2025年最新のAIライティングツール徹底比較",
            "keywords": ["AIライティング", "文章生成", "自動化", "Claude", "ChatGPT"],
            "categories": ["AI", "Technology"],
            "tags": ["ライティング", "AI", "ツール比較"],
            "affiliate_products": [
                {
                    "name": "Claude API",
                    "url": "https://www.anthropic.com/api",
                    "description": "高品質な長文生成に強いAIモデル"
                }
            ]
        },
        {
            "topic": "プログラミング学習に最適なAIアシスタント5選",
            "keywords": ["プログラミング", "AI", "学習", "コーディング"],
            "categories": ["Programming", "AI"],
            "tags": ["プログラミング", "学習", "AIアシスタント"],
            "affiliate_products": []
        },
        {
            "topic": "ブログ運営を自動化する最新AIツール活用術",
            "keywords": ["ブログ", "自動化", "AI", "コンテンツ生成"],
            "categories": ["Blogging", "Automation"],
            "tags": ["ブログ", "自動化", "AI"],
            "affiliate_products": []
        }
    ]


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="GitHub Pages自動アフィリエイトシステム")
    parser.add_argument(
        '--mode',
        choices=['once', 'daemon'],
        default='once',
        help='実行モード: once=1回のみ, daemon=定期実行'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='定期実行間隔（秒）デフォルト: 3600秒（1時間）'
    )
    parser.add_argument(
        '--max-articles',
        type=int,
        default=3,
        help='1回の実行で生成する最大記事数'
    )

    args = parser.parse_args()

    # APIキーチェック
    if not os.getenv("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY が設定されていません")
        sys.exit(1)

    automation = GitHubPagesAutomation()

    logger.info("=== GitHub Pages自動アフィリエイトシステム起動 ===")
    logger.info(f"モード: {args.mode}")
    logger.info(f"最大記事数: {args.max_articles}")

    try:
        if args.mode == 'once':
            # 1回のみ実行
            articles = get_sample_articles()[:args.max_articles]
            results = automation.run_batch(articles)

            success_count = sum(1 for r in results if r["success"])
            logger.info(f"完了: {success_count}/{len(results)} 記事が正常に投稿されました")

        else:
            # 定期実行モード
            logger.info(f"定期実行間隔: {args.interval}秒")

            while True:
                logger.info(f"=== バッチ実行開始: {datetime.now()} ===")

                articles = get_sample_articles()[:args.max_articles]
                results = automation.run_batch(articles)

                success_count = sum(1 for r in results if r["success"])
                logger.info(f"バッチ完了: {success_count}/{len(results)} 記事投稿")
                logger.info(f"次回実行まで {args.interval}秒 待機...")

                time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("ユーザーによる中断")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
