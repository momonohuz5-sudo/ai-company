"""記事生成・投稿の自動スケジューリング

APSchedulerを使って毎日自動実行
"""

import logging
from datetime import datetime, time
from typing import List, Dict
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .config import Config
from .workflow import ArticleWorkflow


class ArticleScheduler:
    """記事自動生成・投稿スケジューラー"""

    # 難易度ローテーション（曜日別）
    # 最初は初心者向け記事を中心に配信
    DIFFICULTY_ROTATION = {
        0: 1,  # 月曜: 初級
        1: 1,  # 火曜: 初級
        2: 2,  # 水曜: 中級
        3: 1,  # 木曜: 初級
        4: 2,  # 金曜: 中級
        5: 3,  # 土曜: 中級（大会レビューまたは通常記事）
        6: 1,  # 日曜: 初級
    }

    # トピックプール（曜日別）
    TOPIC_POOL = {
        # 月曜（初級）
        1: [
            "プリフロップレンジの基本",
            "ポジションの重要性",
            "ポットオッズとエクイティ",
            "ベットサイジングの基礎",
            "ハンド選択の基本",
        ],
        # 中級
        2: [
            "ボードテクスチャ別Cベット戦略",
            "3ベットポット戦略",
            "レンジ対レンジの思考",
            "チェックレイズの効果的な使い方",
            "ポストフロップのエクイティリアライゼーション",
        ],
        # 中級（土曜・日曜用）
        3: [
            "複数人ポットでの戦略調整",
            "ブラインド vs ブラインドの戦い方",
            "スタックサイズ別戦略",
            "テーブルイメージの活用",
            "ティルト防止のメンタル管理",
        ],
        # 上級（火曜）
        4: [
            "GTO最適化戦略とエクスプロイト調整",
            "MDF（Minimum Defense Frequency）の理解と応用",
            "レンジマージとポーラライゼーション",
            "期待値計算とリスク管理",
            "マルチウェイポットのGTO戦略",
        ],
        # 上級（木曜）
        5: [
            "ICMプレッシャー下の意思決定",
            "ファイナルテーブル戦略",
            "ショートスタック vs ビッグスタックの駆け引き",
            "トーナメントのバブル戦略",
            "アンティゲーム時代の調整",
        ],
    }

    def __init__(self, use_mock: bool = False):
        """初期化

        Args:
            use_mock: Trueの場合、実際にnoteに投稿せずモック実行
        """
        self.logger = logging.getLogger(__name__)
        self.workflow = ArticleWorkflow(use_mock=use_mock)
        self.scheduler = BlockingScheduler()
        self.timezone = pytz.timezone(Config.TIMEZONE)
        self.topic_index = {}  # 各難易度の次のトピックインデックス

    def generate_daily_article(self):
        """毎日の記事生成・投稿（スケジューラーから呼ばれる）"""
        try:
            # 曜日取得（0=月曜, 6=日曜）
            now = datetime.now(self.timezone)
            weekday = now.weekday()

            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Daily article generation started")
            self.logger.info(f"Date: {now.strftime('%Y-%m-%d %A')}")
            self.logger.info(f"{'='*60}\n")

            # 難易度決定
            difficulty = self.DIFFICULTY_ROTATION.get(weekday, 2)

            # トピック選択
            topic_list = self.TOPIC_POOL.get(difficulty, self.TOPIC_POOL[2])
            if difficulty not in self.topic_index:
                self.topic_index[difficulty] = 0

            topic = topic_list[self.topic_index[difficulty] % len(topic_list)]
            self.topic_index[difficulty] += 1

            # ハッシュタグ
            hashtags = ["ポーカー", "ポーカー戦略", "GTO"]
            if difficulty <= 2:
                hashtags.append("ポーカー初心者")
            else:
                hashtags.append("ポーカー上級者")

            # 記事生成・投稿
            result = self.workflow.generate_and_publish(
                topic=topic,
                difficulty=difficulty,
                hashtags=hashtags,
                publish_immediately=True,
            )

            if result["success"]:
                self.logger.info(f"\n✓ Daily article published successfully")
                self.logger.info(f"URL: {result['note_url']}")
            else:
                self.logger.error(f"\n✗ Failed to publish daily article: {result['error']}")

        except Exception as e:
            self.logger.error(f"✗ Daily generation failed: {e}", exc_info=True)

    def start(self):
        """スケジューラー開始"""
        # 毎日の投稿時刻を設定
        publish_time = Config.PUBLISH_TIME.split(":")
        hour = int(publish_time[0])
        minute = int(publish_time[1])

        # Cronトリガー（毎日指定時刻）
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=self.timezone,
        )

        self.scheduler.add_job(
            self.generate_daily_article,
            trigger=trigger,
            id="daily_article",
            name="Daily Poker Strategy Article",
            replace_existing=True,
        )

        self.logger.info(f"Scheduler started")
        self.logger.info(f"Daily article will be published at {Config.PUBLISH_TIME} {Config.TIMEZONE}")
        self.logger.info(f"Press Ctrl+C to stop")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Scheduler stopped")

    def run_once(self):
        """1回だけ実行（テスト用）"""
        self.logger.info("Running daily article generation once...")
        self.generate_daily_article()


def main():
    """スケジューラーのメインエントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(description="ポーカー記事自動投稿スケジューラー")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="モックモード（実際には投稿しない）"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="1回だけ実行してテスト"
    )

    args = parser.parse_args()

    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # スケジューラー起動
    scheduler = ArticleScheduler(use_mock=args.mock)

    if args.once:
        scheduler.run_once()
    else:
        scheduler.start()


if __name__ == "__main__":
    main()
