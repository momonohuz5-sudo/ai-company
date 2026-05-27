"""
キーワード分析モジュール
収集したトレンドからアフィリエイト適性の高いキーワードを抽出・分析
"""
import json
import os
from typing import List, Dict, Any
from datetime import datetime


class KeywordAnalyzer:
    """キーワードを分析し、アフィリエイト適性を評価するクラス"""

    # 収益性の高いカテゴリキーワード
    HIGH_VALUE_CATEGORIES = [
        '美容', 'ダイエット', '健康', 'サプリ', 'コスメ',
        '転職', '副業', '投資', 'クレジットカード', '保険',
        'ガジェット', 'スマホ', 'PC', '家電',
        '英語', '学習', '資格', 'プログラミング',
        'VOD', '動画配信', 'WiFi', 'サーバー'
    ]

    # 購買意欲の高いキーワード
    BUYING_INTENT_KEYWORDS = [
        'おすすめ', '比較', 'ランキング', '口コミ', 'レビュー',
        '最安', '安い', 'セール', 'キャンペーン',
        '使い方', '選び方', 'どっち', 'どれ',
        '2026', '最新', '人気'
    ]

    def __init__(self):
        self.results_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.results_dir, exist_ok=True)

    def calculate_affiliate_score(self, keyword: str, trend_data: Dict[str, Any]) -> float:
        """
        キーワードのアフィリエイト適性スコアを計算 (0-100)

        評価基準:
        - 高収益カテゴリに属する: +30点
        - 購買意欲キーワードを含む: +20点
        - トレンド上昇中: +20点
        - 商品名を含む: +15点
        - 価格情報あり: +15点
        """
        score = 0.0

        # カテゴリ評価
        for category in self.HIGH_VALUE_CATEGORIES:
            if category in keyword:
                score += 30
                break

        # 購買意欲評価
        for intent_word in self.BUYING_INTENT_KEYWORDS:
            if intent_word in keyword:
                score += 20
                break

        # トレンド評価
        source = trend_data.get('source', '')
        if 'bestseller' in source or 'ranking' in source:
            score += 20

        # 商品名評価（具体的な商品名が含まれているか）
        if any(char.isdigit() for char in keyword) or len(keyword.split()) >= 3:
            score += 15

        # 価格情報評価
        if trend_data.get('price'):
            score += 15

        return min(score, 100.0)

    def analyze_trends(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        トレンドリストを分析し、アフィリエイト適性スコアを付与

        Args:
            trends: トレンドデータのリスト

        Returns:
            スコア付きトレンドリスト（降順ソート）
        """
        analyzed = []

        for trend in trends:
            keyword = trend.get('keyword', '')
            if not keyword:
                continue

            score = self.calculate_affiliate_score(keyword, trend)

            analyzed.append({
                **trend,
                'affiliate_score': score,
                'analyzed_at': datetime.now().isoformat()
            })

        # スコアの高い順にソート
        analyzed.sort(key=lambda x: x['affiliate_score'], reverse=True)

        return analyzed

    def filter_high_potential_keywords(
        self,
        trends: List[Dict[str, Any]],
        min_score: float = 50.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        高ポテンシャルのキーワードを抽出

        Args:
            trends: 分析済みトレンドリスト
            min_score: 最小スコア閾値
            limit: 最大取得件数

        Returns:
            フィルタ済みキーワードリスト
        """
        filtered = [
            trend for trend in trends
            if trend.get('affiliate_score', 0) >= min_score
        ]

        return filtered[:limit]

    def generate_article_topics(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        キーワードから記事タイトル案を生成

        Args:
            keywords: キーワードリスト

        Returns:
            記事トピックリスト
        """
        topics = []

        title_templates = [
            "【2026年最新】{keyword}おすすめランキングTOP10",
            "{keyword}徹底比較！人気の理由と選び方",
            "{keyword}の口コミ・評判まとめ｜実際に使ってみた",
            "【保存版】{keyword}完全ガイド｜初心者でもわかる選び方",
            "{keyword}を安く買う方法｜お得なキャンペーン情報"
        ]

        for keyword_data in keywords:
            keyword = keyword_data.get('keyword', '')

            # 各テンプレートでタイトル生成
            for template in title_templates[:2]:  # 各キーワードにつき2パターン
                title = template.format(keyword=keyword)

                topics.append({
                    'keyword': keyword,
                    'title': title,
                    'affiliate_score': keyword_data.get('affiliate_score', 0),
                    'source_data': keyword_data,
                    'created_at': datetime.now().isoformat()
                })

        return topics

    def save_analysis_results(self, analyzed_trends: List[Dict[str, Any]], filename: str = None):
        """分析結果を保存"""
        if not filename:
            filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.results_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'analyzed_at': datetime.now().isoformat(),
                'total_count': len(analyzed_trends),
                'high_score_count': len([t for t in analyzed_trends if t.get('affiliate_score', 0) >= 70]),
                'trends': analyzed_trends
            }, f, ensure_ascii=False, indent=2)

        print(f"分析結果を保存しました: {filepath}")
        return filepath


if __name__ == '__main__':
    from trend_collector import TrendCollector

    # トレンド収集
    collector = TrendCollector()
    trends = collector.collect_all_trends(save=False)

    # キーワード分析
    analyzer = KeywordAnalyzer()
    analyzed = analyzer.analyze_trends(trends)

    # 高ポテンシャルキーワード抽出
    high_potential = analyzer.filter_high_potential_keywords(analyzed, min_score=50)

    # 記事トピック生成
    topics = analyzer.generate_article_topics(high_potential[:5])

    print("\n=== 高ポテンシャルキーワード ===")
    for i, trend in enumerate(high_potential[:10], 1):
        print(f"{i}. {trend['keyword']} (スコア: {trend['affiliate_score']:.1f})")

    print("\n=== 記事トピック案 ===")
    for i, topic in enumerate(topics[:5], 1):
        print(f"{i}. {topic['title']}")

    # 結果保存
    analyzer.save_analysis_results(analyzed)
