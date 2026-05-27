#!/usr/bin/env python3
"""
GitHub Pages向け記事生成モジュール
Claude APIを使用してSEO最適化されたアフィリエイト記事を生成
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class GitHubPagesArticleGenerator:
    """GitHub Pages向けアフィリエイト記事生成クラス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Anthropic APIキー（Noneの場合は環境変数から取得）
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"

    def generate_article(
        self,
        topic: str,
        keywords: List[str],
        target_length: int = 3000,
        affiliate_products: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, any]:
        """
        アフィリエイト記事を生成

        Args:
            topic: 記事のトピック
            keywords: SEOキーワードリスト
            target_length: 目標文字数
            affiliate_products: アフィリエイト商品情報リスト

        Returns:
            生成された記事情報
        """
        # システムプロンプト（プロンプトキャッシュ対象）
        system_prompt = [
            {
                "type": "text",
                "text": """あなたはSEO最適化とアフィリエイトマーケティングの専門家です。
読者に価値を提供しつつ、自然な形でアフィリエイト商品を紹介する記事を作成してください。

記事作成のガイドライン:
1. タイトルはSEOを意識し、キーワードを含める
2. 見出し構造（H2, H3）を適切に使用
3. 読みやすい段落構成
4. 具体的な情報と実用的なアドバイス
5. アフィリエイトリンクは自然に組み込む
6. 記事の最後に「まとめ」セクションを追加
7. Markdown形式で出力
8. 文字数は{target_length}文字程度を目標""",
                "cache_control": {"type": "ephemeral"}
            }
        ]

        # アフィリエイト商品情報を整形
        products_text = ""
        if affiliate_products:
            products_text = "\n\n紹介する商品:\n"
            for i, product in enumerate(affiliate_products, 1):
                products_text += f"{i}. {product.get('name', '商品名未設定')}\n"
                products_text += f"   URL: {product.get('url', '#')}\n"
                products_text += f"   特徴: {product.get('description', '説明なし')}\n"

        # ユーザープロンプト
        user_prompt = f"""以下のトピックについて、SEO最適化されたアフィリエイト記事を作成してください。

トピック: {topic}

SEOキーワード: {', '.join(keywords)}

目標文字数: {target_length}文字
{products_text}

記事は以下の構造で作成してください:
1. 導入（問題提起・読者の共感）
2. 本論（情報提供・解決策）
3. 商品紹介（自然な流れで）
4. まとめ（行動喚起）

Markdown形式で、見出し・リスト・強調を適切に使用してください。"""

        try:
            # Claude APIで記事生成
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            article_content = response.content[0].text

            # タイトルを抽出（最初のH1見出し）
            title_line = article_content.split('\n')[0]
            title = title_line.replace('# ', '').strip() if title_line.startswith('#') else topic

            # 本文（タイトル行を除く）
            content_without_title = '\n'.join(article_content.split('\n')[1:]).strip()

            # 要約を生成（最初の段落）
            excerpt = content_without_title.split('\n\n')[0][:200] + "..."

            logger.info(f"記事生成成功: {title}")

            return {
                "success": True,
                "title": title,
                "content": content_without_title,
                "full_content": article_content,
                "excerpt": excerpt,
                "keywords": keywords,
                "word_count": len(article_content),
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cache_creation_input_tokens": getattr(response.usage, 'cache_creation_input_tokens', 0),
                    "cache_read_input_tokens": getattr(response.usage, 'cache_read_input_tokens', 0)
                }
            }

        except Exception as e:
            logger.error(f"記事生成エラー: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def test_generator():
    """テスト用関数"""
    generator = GitHubPagesArticleGenerator()

    # サンプル記事生成
    result = generator.generate_article(
        topic="2025年最新のAIライティングツール比較",
        keywords=["AIライティング", "文章生成", "自動化", "Claude"],
        target_length=2000,
        affiliate_products=[
            {
                "name": "Claude API",
                "url": "https://www.anthropic.com/api",
                "description": "最先端のAI言語モデル"
            }
        ]
    )

    if result["success"]:
        print(f"タイトル: {result['title']}")
        print(f"文字数: {result['word_count']}")
        print(f"トークン使用量: {result['usage']}")
        print("\n--- 記事内容（抜粋） ---")
        print(result['content'][:500])
    else:
        print(f"エラー: {result['error']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_generator()
