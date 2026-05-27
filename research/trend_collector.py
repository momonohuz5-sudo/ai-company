"""
トレンド収集モジュール
Googleトレンド、Amazon売れ筋、楽天ランキングからトレンドキーワードを収集
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from pytrends.request import TrendReq
from bs4 import BeautifulSoup


class TrendCollector:
    """トレンド情報を収集するクラス"""

    def __init__(self):
        self.pytrends = TrendReq(hl='ja-JP', tz=360)
        self.results_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.results_dir, exist_ok=True)

    def collect_google_trends(self, category: str = None, count: int = 20) -> List[Dict[str, Any]]:
        """
        Googleトレンドから急上昇キーワードを取得

        Args:
            category: カテゴリ (例: 'tech', 'lifestyle', 'business')
            count: 取得件数

        Returns:
            トレンドキーワードのリスト
        """
        try:
            trends_df = self.pytrends.trending_searches(pn='japan')
            keywords = trends_df[0].tolist()[:count]

            results = []
            for keyword in keywords:
                results.append({
                    'keyword': keyword,
                    'source': 'google_trends',
                    'category': category or 'general',
                    'timestamp': datetime.now().isoformat(),
                    'search_volume': 'rising'
                })

            return results
        except Exception as e:
            print(f"Google Trends収集エラー: {e}")
            return []

    def collect_amazon_bestsellers(self, category: str = 'all', count: int = 20) -> List[Dict[str, Any]]:
        """
        Amazon売れ筋ランキングから商品情報を取得（スクレイピング）

        Args:
            category: Amazonカテゴリ
            count: 取得件数

        Returns:
            商品情報のリスト
        """
        categories = {
            'electronics': 'electronics',
            'books': 'books',
            'home': 'home-garden',
            'all': 'bestsellers'
        }

        category_path = categories.get(category, 'bestsellers')
        url = f"https://www.amazon.co.jp/gp/{category_path}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            results = []
            items = soup.select('.zg-item-immersion')[:count]

            for item in items:
                title_elem = item.select_one('.p13n-sc-truncate')
                if title_elem:
                    results.append({
                        'keyword': title_elem.get_text(strip=True),
                        'source': 'amazon_bestsellers',
                        'category': category,
                        'timestamp': datetime.now().isoformat(),
                        'rank_type': 'bestseller'
                    })

            return results
        except Exception as e:
            print(f"Amazon収集エラー: {e}")
            return []

    def collect_rakuten_ranking(self, genre_id: str = None, count: int = 20) -> List[Dict[str, Any]]:
        """
        楽天ランキングAPIから商品情報を取得

        Args:
            genre_id: 楽天ジャンルID
            count: 取得件数

        Returns:
            商品情報のリスト
        """
        app_id = os.getenv('RAKUTEN_APP_ID')
        if not app_id:
            print("楽天API IDが設定されていません")
            return []

        url = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20170628"
        params = {
            'applicationId': app_id,
            'genreId': genre_id or '0',
            'count': min(count, 30)
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            results = []
            for item in data.get('Items', []):
                item_data = item.get('Item', {})
                results.append({
                    'keyword': item_data.get('itemName', ''),
                    'source': 'rakuten_ranking',
                    'category': genre_id or 'general',
                    'timestamp': datetime.now().isoformat(),
                    'rank': item_data.get('rank'),
                    'price': item_data.get('itemPrice'),
                    'url': item_data.get('itemUrl')
                })

            return results
        except Exception as e:
            print(f"楽天ランキング収集エラー: {e}")
            return []

    def save_trends(self, trends: List[Dict[str, Any]], filename: str = None):
        """トレンドデータをJSONファイルに保存"""
        if not filename:
            filename = f"trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.results_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'collected_at': datetime.now().isoformat(),
                'total_count': len(trends),
                'trends': trends
            }, f, ensure_ascii=False, indent=2)

        print(f"トレンドデータを保存しました: {filepath}")
        return filepath

    def get_latest_trends(self, limit: int = 10) -> List[Dict[str, Any]]:
        """最新のトレンドデータを取得"""
        files = sorted([
            f for f in os.listdir(self.results_dir)
            if f.startswith('trends_') and f.endswith('.json')
        ], reverse=True)

        if not files:
            return []

        latest_file = os.path.join(self.results_dir, files[0])
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('trends', [])[:limit]

    def collect_all_trends(self, save: bool = True) -> List[Dict[str, Any]]:
        """全ソースからトレンドを収集"""
        print("トレンド収集を開始します...")

        all_trends = []

        # Googleトレンド
        print("Googleトレンドを収集中...")
        google_trends = self.collect_google_trends(count=10)
        all_trends.extend(google_trends)

        # Amazon売れ筋
        print("Amazon売れ筋を収集中...")
        amazon_trends = self.collect_amazon_bestsellers(category='all', count=10)
        all_trends.extend(amazon_trends)

        # 楽天ランキング
        print("楽天ランキングを収集中...")
        rakuten_trends = self.collect_rakuten_ranking(count=10)
        all_trends.extend(rakuten_trends)

        print(f"合計 {len(all_trends)} 件のトレンドを収集しました")

        if save:
            self.save_trends(all_trends)

        return all_trends


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    collector = TrendCollector()
    trends = collector.collect_all_trends()

    print("\n=== 収集結果 ===")
    for i, trend in enumerate(trends[:5], 1):
        print(f"{i}. {trend['keyword']} (出典: {trend['source']})")
