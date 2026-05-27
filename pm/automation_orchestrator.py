"""
自動化オーケストレーター
全部門のモジュールを統合し、24時間自動運用を実現
"""
import os
import sys
import json
import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 各部門のモジュールをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'research'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dev'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'marketing'))

from research.trend_collector import TrendCollector
from research.keyword_analyzer import KeywordAnalyzer
from dev.article_generator import ArticleGenerator
from dev.wordpress_publisher import WordPressPublisher
from marketing.content_scheduler import ContentScheduler, PerformanceAnalyzer


class AutomationOrchestrator:
    """AIアフィリエイト記事自動生成システムのオーケストレーター"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初期化

        Args:
            config: システム設定
        """
        self.config = config or self._load_default_config()

        # 各部門のモジュール初期化
        self.trend_collector = TrendCollector()
        self.keyword_analyzer = KeywordAnalyzer()
        self.article_generator = ArticleGenerator()
        self.scheduler = ContentScheduler()
        self.analyzer = PerformanceAnalyzer()

        # WordPress Publisher（オプション）
        self.wp_publisher = None
        if self.config.get('wordpress_enabled'):
            try:
                self.wp_publisher = WordPressPublisher()
            except Exception as e:
                print(f"WordPress接続エラー: {e}")

        # ログディレクトリ
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)

    def _load_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を読み込み"""
        return {
            'auto_post_enabled': os.getenv('AUTO_POST_ENABLED', 'false').lower() == 'true',
            'wordpress_enabled': bool(os.getenv('WORDPRESS_URL')),
            'post_interval_hours': int(os.getenv('POST_INTERVAL_HOURS', '24')),
            'max_articles_per_day': int(os.getenv('MAX_ARTICLES_PER_DAY', '3')),
            'min_affiliate_score': 60.0,
            'article_target_length': 3000,
            'trend_collection_interval': 6,  # 6時間ごと
        }

    def run_trend_collection_pipeline(self) -> List[Dict[str, Any]]:
        """
        トレンド収集パイプライン

        Returns:
            高ポテンシャルのキーワードリスト
        """
        print("\n" + "="*60)
        print("【トレンド収集パイプライン】開始")
        print("="*60)

        # 1. トレンド収集
        print("\n[1/3] トレンド収集中...")
        trends = self.trend_collector.collect_all_trends(save=True)
        print(f"✓ {len(trends)}件のトレンドを収集")

        # 2. キーワード分析
        print("\n[2/3] キーワード分析中...")
        analyzed = self.keyword_analyzer.analyze_trends(trends)
        self.keyword_analyzer.save_analysis_results(analyzed)
        print(f"✓ {len(analyzed)}件のキーワードを分析")

        # 3. 高ポテンシャルキーワード抽出
        print("\n[3/3] 高ポテンシャルキーワード抽出中...")
        high_potential = self.keyword_analyzer.filter_high_potential_keywords(
            analyzed,
            min_score=self.config['min_affiliate_score']
        )
        print(f"✓ {len(high_potential)}件の高ポテンシャルキーワードを抽出")

        # ログ保存
        self._save_pipeline_log('trend_collection', {
            'total_trends': len(trends),
            'analyzed_keywords': len(analyzed),
            'high_potential_count': len(high_potential)
        })

        return high_potential

    def run_article_generation_pipeline(
        self,
        keywords: List[Dict[str, Any]],
        max_count: int = None
    ) -> List[Dict[str, Any]]:
        """
        記事生成パイプライン

        Args:
            keywords: キーワードリスト
            max_count: 最大生成数

        Returns:
            生成された記事リスト
        """
        print("\n" + "="*60)
        print("【記事生成パイプライン】開始")
        print("="*60)

        max_count = max_count or self.config['max_articles_per_day']

        # 1. 記事トピック生成
        print("\n[1/2] 記事トピック生成中...")
        topics = self.keyword_analyzer.generate_article_topics(keywords[:max_count])
        print(f"✓ {len(topics)}件のトピックを生成")

        # 2. 記事生成
        print("\n[2/2] AI記事生成中...")
        articles = self.article_generator.batch_generate_articles(
            topics,
            max_count=max_count
        )
        print(f"✓ {len(articles)}件の記事を生成")

        # ログ保存
        self._save_pipeline_log('article_generation', {
            'topics_generated': len(topics),
            'articles_generated': len(articles)
        })

        return articles

    def run_publishing_pipeline(
        self,
        articles: List[Dict[str, Any]],
        auto_publish: bool = None
    ) -> List[Dict[str, Any]]:
        """
        投稿パイプライン

        Args:
            articles: 記事リスト
            auto_publish: 自動公開するか

        Returns:
            投稿結果リスト
        """
        print("\n" + "="*60)
        print("【投稿パイプライン】開始")
        print("="*60)

        if auto_publish is None:
            auto_publish = self.config['auto_post_enabled']

        results = []

        if self.wp_publisher:
            # WordPressに投稿
            print("\n[1/1] WordPress投稿中...")
            results = self.wp_publisher.batch_publish_articles(
                articles,
                auto_publish=auto_publish
            )
            print(f"✓ {len(results)}件を投稿")
        else:
            print("\nWordPress未設定のため、ローカル保存のみ")
            results = articles

        # ログ保存
        self._save_pipeline_log('publishing', {
            'articles_published': len(results),
            'auto_publish': auto_publish
        })

        return results

    def run_full_automation_cycle(self):
        """フル自動化サイクルを実行"""
        print("\n" + "="*70)
        print(" "*20 + "【自動化サイクル】開始")
        print("="*70)
        start_time = datetime.now()

        try:
            # 1. トレンド収集
            keywords = self.run_trend_collection_pipeline()

            if not keywords:
                print("\n高ポテンシャルキーワードが見つかりませんでした")
                return

            # 2. 記事生成
            articles = self.run_article_generation_pipeline(keywords)

            if not articles:
                print("\n記事生成に失敗しました")
                return

            # 3. 投稿
            results = self.run_publishing_pipeline(articles)

            # サマリー表示
            elapsed = datetime.now() - start_time
            print("\n" + "="*70)
            print("【自動化サイクル】完了")
            print("="*70)
            print(f"処理時間: {elapsed}")
            print(f"キーワード収集: {len(keywords)}件")
            print(f"記事生成: {len(articles)}件")
            print(f"投稿: {len(results)}件")
            print("="*70)

        except Exception as e:
            print(f"\n自動化サイクルエラー: {e}")
            self._save_error_log(str(e))

    def start_scheduler(self):
        """スケジューラーを起動して24時間自動運用"""
        print("\n" + "="*70)
        print(" "*15 + "【24時間自動運用モード】起動")
        print("="*70)

        interval_hours = self.config['post_interval_hours']

        # 定期実行スケジュール
        schedule.every(interval_hours).hours.do(self.run_full_automation_cycle)

        # トレンド収集のみ（より頻繁に）
        schedule.every(self.config['trend_collection_interval']).hours.do(
            self.run_trend_collection_pipeline
        )

        print(f"\n⏰ スケジュール設定:")
        print(f"  - フル自動化サイクル: {interval_hours}時間ごと")
        print(f"  - トレンド収集: {self.config['trend_collection_interval']}時間ごと")
        print(f"\n🚀 システム稼働中... (Ctrl+C で停止)\n")

        # 初回実行
        self.run_full_automation_cycle()

        # スケジューラーループ
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
        except KeyboardInterrupt:
            print("\n\nシステムを停止しました")

    def _save_pipeline_log(self, pipeline_name: str, data: Dict[str, Any]):
        """パイプラインログを保存"""
        log_file = os.path.join(self.log_dir, 'pipeline_logs.json')

        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append({
            'pipeline': pipeline_name,
            'timestamp': datetime.now().isoformat(),
            **data
        })

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def _save_error_log(self, error_message: str):
        """エラーログを保存"""
        log_file = os.path.join(self.log_dir, 'error_logs.json')

        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append({
            'timestamp': datetime.now().isoformat(),
            'error': error_message
        })

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        scheduler_summary = self.scheduler.get_schedule_summary()

        return {
            'status': 'running',
            'config': self.config,
            'scheduler': scheduler_summary,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    import argparse

    parser = argparse.ArgumentParser(description='AIアフィリエイト記事自動生成システム')
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

    args = parser.parse_args()

    orchestrator = AutomationOrchestrator()

    if args.mode == 'daemon':
        # 24時間自動運用モード
        orchestrator.start_scheduler()
    else:
        # 1回のみ実行
        if args.skip_publish:
            # 記事生成まで
            keywords = orchestrator.run_trend_collection_pipeline()
            orchestrator.run_article_generation_pipeline(keywords)
        else:
            # フルサイクル実行
            orchestrator.run_full_automation_cycle()
