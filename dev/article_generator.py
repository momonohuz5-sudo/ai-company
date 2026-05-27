"""
AI記事生成モジュール
Claude APIを使用してSEO最適化されたアフィリエイト記事を自動生成
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from anthropic import Anthropic


class ArticleGenerator:
    """Claude APIを使用して記事を生成するクラス"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"
        self.results_dir = os.path.join(os.path.dirname(__file__), 'articles')
        os.makedirs(self.results_dir, exist_ok=True)

    def create_article_prompt(
        self,
        keyword: str,
        title: str,
        affiliate_links: List[Dict[str, str]] = None,
        target_length: int = 3000
    ) -> str:
        """
        記事生成用のプロンプトを作成

        Args:
            keyword: ターゲットキーワード
            title: 記事タイトル
            affiliate_links: アフィリエイトリンク情報
            target_length: 目標文字数

        Returns:
            プロンプト文字列
        """
        affiliate_info = ""
        if affiliate_links:
            affiliate_info = "\n\n【紹介する商品/サービス】\n"
            for i, link in enumerate(affiliate_links, 1):
                affiliate_info += f"{i}. {link.get('name', '')} - {link.get('url', '')}\n"

        prompt = f"""あなたはプロのアフィリエイトライターです。以下の条件で高品質なアフィリエイト記事を作成してください。

【記事タイトル】
{title}

【ターゲットキーワード】
{keyword}

【記事の要件】
- 文字数: 約{target_length}文字
- SEOを意識した構成（見出しタグの適切な使用）
- 読者の購買意欲を高める内容
- 信頼性のある情報提供
- 自然な形でのアフィリエイトリンク配置
- 初心者にもわかりやすい説明
{affiliate_info}

【記事構成の例】
1. 導入（問題提起・共感）
2. {keyword}とは？基礎知識
3. {keyword}の選び方・比較ポイント
4. おすすめ{keyword}ランキング（商品紹介）
5. よくある質問（FAQ）
6. まとめ（CTA）

【記事の形式】
- Markdown形式で出力
- 見出しは ## から開始（# は使わない）
- 箇条書きやテーブルを適切に使用
- 読みやすい段落構成

上記の要件に従って、読者に価値を提供する記事を作成してください。
"""
        return prompt

    def generate_article(
        self,
        keyword: str,
        title: str,
        affiliate_links: List[Dict[str, str]] = None,
        target_length: int = 3000,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        記事を生成

        Args:
            keyword: ターゲットキーワード
            title: 記事タイトル
            affiliate_links: アフィリエイトリンク情報
            target_length: 目標文字数
            use_cache: プロンプトキャッシュを使用するか

        Returns:
            生成された記事データ
        """
        print(f"記事生成中: {title}")

        prompt = self.create_article_prompt(keyword, title, affiliate_links, target_length)

        try:
            # Claude APIで記事生成
            if use_cache:
                # プロンプトキャッシュを使用して効率化
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8000,
                    system=[
                        {
                            "type": "text",
                            "text": "あなたはプロのSEOライター兼アフィリエイトマーケターです。高品質で読者に価値を提供する記事を作成します。",
                            "cache_control": {"type": "ephemeral"}
                        }
                    ],
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

            article_content = response.content[0].text

            article_data = {
                'title': title,
                'keyword': keyword,
                'content': article_content,
                'word_count': len(article_content),
                'affiliate_links': affiliate_links or [],
                'generated_at': datetime.now().isoformat(),
                'model': self.model,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }

            print(f"記事生成完了: {len(article_content)} 文字")
            return article_data

        except Exception as e:
            print(f"記事生成エラー: {e}")
            raise

    def generate_seo_metadata(self, article_data: Dict[str, Any]) -> Dict[str, str]:
        """
        記事のSEOメタデータを生成

        Args:
            article_data: 記事データ

        Returns:
            SEOメタデータ
        """
        keyword = article_data.get('keyword', '')
        title = article_data.get('title', '')
        content = article_data.get('content', '')

        # 記事の最初の部分から説明文を生成
        lines = content.split('\n')
        description_text = ''
        for line in lines:
            if line.strip() and not line.startswith('#'):
                description_text = line.strip()[:150]
                break

        metadata = {
            'meta_title': f"{title} | 2026年最新情報",
            'meta_description': description_text or f"{keyword}について詳しく解説。おすすめ商品の比較・選び方・口コミなど、購入前に知っておきたい情報をまとめました。",
            'meta_keywords': f"{keyword}, おすすめ, ランキング, 比較, 口コミ, 2026",
            'og_title': title,
            'og_description': description_text or f"{keyword}の最新情報",
            'og_type': 'article'
        }

        return metadata

    def save_article(self, article_data: Dict[str, Any], filename: str = None) -> str:
        """
        記事をファイルに保存

        Args:
            article_data: 記事データ
            filename: ファイル名（省略時は自動生成）

        Returns:
            保存先ファイルパス
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_keyword = article_data.get('keyword', 'article').replace('/', '_')[:30]
            filename = f"{timestamp}_{safe_keyword}.json"

        filepath = os.path.join(self.results_dir, filename)

        # SEOメタデータを追加
        article_data['seo_metadata'] = self.generate_seo_metadata(article_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)

        print(f"記事を保存しました: {filepath}")

        # Markdown版も保存
        md_filepath = filepath.replace('.json', '.md')
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {article_data['title']}\n\n")
            f.write(article_data['content'])

        print(f"Markdown版を保存しました: {md_filepath}")

        return filepath

    def batch_generate_articles(
        self,
        topics: List[Dict[str, Any]],
        max_count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        複数の記事を一括生成

        Args:
            topics: 記事トピックリスト
            max_count: 最大生成数

        Returns:
            生成された記事リスト
        """
        articles = []

        for i, topic in enumerate(topics[:max_count], 1):
            print(f"\n[{i}/{min(len(topics), max_count)}] 記事生成中...")

            try:
                article = self.generate_article(
                    keyword=topic.get('keyword', ''),
                    title=topic.get('title', ''),
                    affiliate_links=topic.get('affiliate_links'),
                    use_cache=True  # キャッシュを使用してコスト削減
                )

                self.save_article(article)
                articles.append(article)

                print(f"✓ 完了: {article['title']}")

            except Exception as e:
                print(f"✗ エラー: {topic.get('title', '')} - {e}")
                continue

        print(f"\n一括生成完了: {len(articles)}/{max_count} 件")
        return articles


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    # サンプル記事生成
    generator = ArticleGenerator()

    sample_topic = {
        'keyword': 'ワイヤレスイヤホン',
        'title': '【2026年最新】ワイヤレスイヤホンおすすめランキングTOP10',
        'affiliate_links': [
            {'name': 'AirPods Pro', 'url': 'https://amzn.to/example1'},
            {'name': 'Sony WF-1000XM5', 'url': 'https://amzn.to/example2'}
        ]
    }

    article = generator.generate_article(
        keyword=sample_topic['keyword'],
        title=sample_topic['title'],
        affiliate_links=sample_topic['affiliate_links']
    )

    generator.save_article(article)
    print("\n記事生成テスト完了")
