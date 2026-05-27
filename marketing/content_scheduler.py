"""
コンテンツスケジューラー
記事の投稿スケジュールを管理し、最適なタイミングで配信
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import schedule
import time


class ContentScheduler:
    """コンテンツ配信スケジュールを管理するクラス"""

    def __init__(self):
        self.schedule_dir = os.path.join(os.path.dirname(__file__), 'schedules')
        os.makedirs(self.schedule_dir, exist_ok=True)
        self.schedule_file = os.path.join(self.schedule_dir, 'content_schedule.json')

    def load_schedule(self) -> List[Dict[str, Any]]:
        """スケジュールを読み込み"""
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_schedule(self, schedule_data: List[Dict[str, Any]]):
        """スケジュールを保存"""
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)

    def add_to_schedule(
        self,
        article_path: str,
        publish_datetime: datetime,
        category: str = 'general',
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        記事を投稿スケジュールに追加

        Args:
            article_path: 記事ファイルパス
            publish_datetime: 投稿予定日時
            category: カテゴリ
            priority: 優先度（1-10、高いほど優先）

        Returns:
            スケジュールエントリ
        """
        schedule_data = self.load_schedule()

        entry = {
            'id': len(schedule_data) + 1,
            'article_path': article_path,
            'publish_datetime': publish_datetime.isoformat(),
            'category': category,
            'priority': priority,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }

        schedule_data.append(entry)
        self.save_schedule(schedule_data)

        print(f"スケジュール追加: {publish_datetime} - {os.path.basename(article_path)}")
        return entry

    def generate_optimal_schedule(
        self,
        articles: List[str],
        start_date: datetime = None,
        interval_hours: int = 24,
        posts_per_day: int = 1
    ) -> List[Dict[str, Any]]:
        """
        最適な投稿スケジュールを自動生成

        Args:
            articles: 記事ファイルパスのリスト
            start_date: 開始日時
            interval_hours: 投稿間隔（時間）
            posts_per_day: 1日あたりの投稿数

        Returns:
            生成されたスケジュールリスト
        """
        if not start_date:
            start_date = datetime.now() + timedelta(hours=1)

        # 最適な投稿時間帯（エンゲージメントが高い時間）
        optimal_hours = [9, 12, 15, 20]  # 9時, 12時, 15時, 20時

        scheduled = []
        current_date = start_date

        for i, article_path in enumerate(articles):
            # 最適な時間帯を選択
            hour = optimal_hours[i % len(optimal_hours)]

            # 投稿日時を設定
            publish_time = current_date.replace(hour=hour, minute=0, second=0)

            entry = self.add_to_schedule(
                article_path=article_path,
                publish_datetime=publish_time,
                priority=10 - (i % 10)  # 優先度を分散
            )

            scheduled.append(entry)

            # 次の投稿日時を計算
            if (i + 1) % posts_per_day == 0:
                current_date += timedelta(days=1)

        print(f"\n{len(scheduled)}件の記事をスケジュールしました")
        return scheduled

    def get_pending_posts(self) -> List[Dict[str, Any]]:
        """投稿予定の記事を取得"""
        schedule_data = self.load_schedule()
        now = datetime.now()

        pending = [
            entry for entry in schedule_data
            if entry.get('status') == 'scheduled'
            and datetime.fromisoformat(entry['publish_datetime']) <= now
        ]

        return sorted(pending, key=lambda x: x.get('priority', 0), reverse=True)

    def mark_as_published(self, entry_id: int, post_url: str = None):
        """記事を公開済みとしてマーク"""
        schedule_data = self.load_schedule()

        for entry in schedule_data:
            if entry.get('id') == entry_id:
                entry['status'] = 'published'
                entry['published_at'] = datetime.now().isoformat()
                if post_url:
                    entry['post_url'] = post_url
                break

        self.save_schedule(schedule_data)

    def get_schedule_summary(self) -> Dict[str, Any]:
        """スケジュールのサマリーを取得"""
        schedule_data = self.load_schedule()

        total = len(schedule_data)
        scheduled = len([e for e in schedule_data if e.get('status') == 'scheduled'])
        published = len([e for e in schedule_data if e.get('status') == 'published'])
        failed = len([e for e in schedule_data if e.get('status') == 'failed'])

        return {
            'total': total,
            'scheduled': scheduled,
            'published': published,
            'failed': failed,
            'next_publish': self._get_next_publish_time(schedule_data)
        }

    def _get_next_publish_time(self, schedule_data: List[Dict[str, Any]]) -> Optional[str]:
        """次の投稿予定時刻を取得"""
        now = datetime.now()

        upcoming = [
            entry for entry in schedule_data
            if entry.get('status') == 'scheduled'
            and datetime.fromisoformat(entry['publish_datetime']) > now
        ]

        if upcoming:
            next_entry = min(upcoming, key=lambda x: x['publish_datetime'])
            return next_entry['publish_datetime']

        return None


class PerformanceAnalyzer:
    """記事のパフォーマンスを分析するクラス"""

    def __init__(self):
        self.analytics_dir = os.path.join(os.path.dirname(__file__), 'analytics')
        os.makedirs(self.analytics_dir, exist_ok=True)

    def track_article_performance(
        self,
        article_id: str,
        metrics: Dict[str, Any]
    ):
        """
        記事のパフォーマンスを記録

        Args:
            article_id: 記事ID
            metrics: メトリクス（PV, CTR, CVなど）
        """
        analytics_file = os.path.join(self.analytics_dir, 'performance.json')

        # 既存データ読み込み
        data = {}
        if os.path.exists(analytics_file):
            with open(analytics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

        # 記事のパフォーマンス更新
        if article_id not in data:
            data[article_id] = []

        data[article_id].append({
            **metrics,
            'recorded_at': datetime.now().isoformat()
        })

        # 保存
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def generate_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートを生成"""
        analytics_file = os.path.join(self.analytics_dir, 'performance.json')

        if not os.path.exists(analytics_file):
            return {'message': 'データがありません'}

        with open(analytics_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 集計
        total_articles = len(data)
        total_views = 0
        total_clicks = 0

        for article_id, metrics_list in data.items():
            if metrics_list:
                latest = metrics_list[-1]
                total_views += latest.get('page_views', 0)
                total_clicks += latest.get('affiliate_clicks', 0)

        avg_ctr = (total_clicks / total_views * 100) if total_views > 0 else 0

        report = {
            'total_articles': total_articles,
            'total_page_views': total_views,
            'total_affiliate_clicks': total_clicks,
            'average_ctr': round(avg_ctr, 2),
            'generated_at': datetime.now().isoformat()
        }

        return report


if __name__ == '__main__':
    # スケジューラーテスト
    scheduler = ContentScheduler()

    # サンプル記事パス
    sample_articles = [
        '/home/user/ai-company/dev/articles/article1.json',
        '/home/user/ai-company/dev/articles/article2.json',
        '/home/user/ai-company/dev/articles/article3.json'
    ]

    # スケジュール生成
    schedule_entries = scheduler.generate_optimal_schedule(
        articles=sample_articles,
        start_date=datetime.now() + timedelta(hours=2),
        posts_per_day=2
    )

    # サマリー表示
    summary = scheduler.get_schedule_summary()
    print("\n=== スケジュールサマリー ===")
    print(f"合計: {summary['total']}件")
    print(f"予定: {summary['scheduled']}件")
    print(f"公開済み: {summary['published']}件")
    print(f"次回投稿: {summary['next_publish']}")
