"""記事生成から投稿までの統合ワークフロー"""

import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

from .config import Config
from .content_generator import ContentGenerator
from .range_chart_renderer import RangeChartRenderer
from .note_publisher import NotePublisher, MockNotePublisher, NOTE_CLIENT_AVAILABLE


class ArticleWorkflow:
    """記事生成・投稿ワークフロー"""

    def __init__(self, use_mock: bool = False):
        """初期化

        Args:
            use_mock: Trueの場合、実際にnoteに投稿せずモック実行
        """
        self.logger = logging.getLogger(__name__)

        # 各コンポーネント初期化
        self.content_generator = ContentGenerator()
        self.chart_renderer = RangeChartRenderer()

        # Note Publisherの選択
        if use_mock or not NOTE_CLIENT_AVAILABLE:
            self.logger.info("Using MockNotePublisher (safe mode)")
            self.note_publisher = MockNotePublisher()
        else:
            self.logger.info("Using NotePublisher (live mode)")
            self.note_publisher = NotePublisher()

    def generate_and_publish(
        self,
        topic: str,
        difficulty: int = 2,
        specific_scenario: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        publish_immediately: bool = True,
    ) -> Dict[str, any]:
        """記事を生成してnoteに投稿

        Args:
            topic: トピック
            difficulty: 難易度 1-5
            specific_scenario: 具体的なシナリオ
            hashtags: ハッシュタグのリスト
            publish_immediately: Trueで即座投稿、Falseで下書き保存のみ

        Returns:
            Dict: {
                "success": bool,
                "article": Dict,
                "chart_paths": List[Path],
                "note_url": str or None,
                "error": str or None,
            }
        """
        result = {
            "success": False,
            "article": None,
            "chart_paths": [],
            "note_url": None,
            "error": None,
        }

        try:
            # ステップ1: 記事生成
            self.logger.info(f"Step 1: Generating article - {topic} (difficulty: {difficulty})")
            article = self.content_generator.generate_article(
                topic=topic,
                difficulty=difficulty,
                specific_scenario=specific_scenario,
                include_chart=True,
            )
            result["article"] = article

            # ステップ2: レンジチャート生成
            chart_paths = []
            if article.get("chart_data"):
                self.logger.info("Step 2: Rendering range chart")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                chart_path = Config.IMAGES_DIR / f"{timestamp}_range_chart.png"

                self.chart_renderer.render_chart(
                    range_data=article["chart_data"]["range_data"],
                    title=article["chart_data"]["chart_title"],
                    output_path=chart_path,
                )
                chart_paths.append(chart_path)
                self.logger.info(f"✓ Chart saved: {chart_path}")

            result["chart_paths"] = chart_paths

            # ステップ3: Markdown保存（バックアップ）
            self.logger.info("Step 3: Saving article backup")
            markdown_path = self.content_generator.save_article(article)
            self.logger.info(f"✓ Backup saved: {markdown_path}")

            # ステップ4: note投稿
            if publish_immediately:
                self.logger.info("Step 4: Publishing to note")

                # デフォルトハッシュタグ
                if hashtags is None:
                    hashtags = ["ポーカー", "ポーカー戦略", "GTO"]

                # 投稿
                publish_result = self.note_publisher.publish_article(
                    title=article["title"],
                    content=article["content"],
                    price=Config.NOTE_ARTICLE_PRICE,
                    images=chart_paths,
                    hashtags=hashtags,
                )

                if publish_result["success"]:
                    result["note_url"] = publish_result["url"]
                    result["success"] = True
                    self.logger.info(f"✓ Published: {publish_result['url']}")
                else:
                    result["error"] = publish_result["error"]
                    self.logger.error(f"✗ Publishing failed: {publish_result['error']}")
            else:
                result["success"] = True
                self.logger.info("✓ Article generated (not published)")

            return result

        except Exception as e:
            self.logger.error(f"✗ Workflow failed: {e}", exc_info=True)
            result["error"] = str(e)
            return result

    def batch_generate(
        self,
        topics: List[Dict[str, any]],
        publish: bool = False,
    ) -> List[Dict[str, any]]:
        """複数記事を一括生成

        Args:
            topics: トピックのリスト [{"topic": str, "difficulty": int, ...}, ...]
            publish: Trueで投稿、Falseで生成のみ

        Returns:
            List[Dict]: 各記事の結果
        """
        results = []

        for i, topic_config in enumerate(topics, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Batch {i}/{len(topics)}")
            self.logger.info(f"{'='*60}\n")

            result = self.generate_and_publish(
                topic=topic_config["topic"],
                difficulty=topic_config.get("difficulty", 2),
                specific_scenario=topic_config.get("specific_scenario"),
                hashtags=topic_config.get("hashtags"),
                publish_immediately=publish,
            )

            results.append(result)

            # レート制限対策（APIキー保護）
            if i < len(topics):
                self.logger.info("Waiting 5 seconds before next article...")
                import time
                time.sleep(5)

        # サマリー
        success_count = sum(1 for r in results if r["success"])
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Batch complete: {success_count}/{len(topics)} succeeded")
        self.logger.info(f"{'='*60}\n")

        return results


# 週間スケジュールのサンプル
WEEKLY_TOPICS = [
    # 月曜日（初級）
    {
        "topic": "プリフロップレンジの基本",
        "difficulty": 1,
        "specific_scenario": "初心者のためのポジション別スタートハンド選択",
        "hashtags": ["ポーカー初心者", "プリフロップ", "ハンド選択"],
    },
    # 火曜日（上級）
    {
        "topic": "GTO最適化戦略",
        "difficulty": 4,
        "specific_scenario": "3ベットポットでのバランス調整とエクスプロイト",
        "hashtags": ["GTO", "ポーカー上級", "3ベット"],
    },
    # 水曜日（中級）
    {
        "topic": "ボードテクスチャ別Cベット戦略",
        "difficulty": 2,
        "specific_scenario": "ドライボード vs ウェットボードのアプローチ",
        "hashtags": ["Cベット", "ボードリーディング", "ポストフロップ"],
    },
    # 木曜日（上級）
    {
        "topic": "ICMプレッシャー下の意思決定",
        "difficulty": 5,
        "specific_scenario": "ファイナルテーブルでの期待値計算とリスク管理",
        "hashtags": ["ICM", "トーナメント", "ファイナルテーブル"],
    },
    # 金曜日（初級）
    {
        "topic": "ポットオッズとエクイティ計算",
        "difficulty": 1,
        "specific_scenario": "初心者でもわかるコール判断の基礎",
        "hashtags": ["ポットオッズ", "エクイティ", "ポーカー数学"],
    },
]
