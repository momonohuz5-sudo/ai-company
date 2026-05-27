#!/usr/bin/env python3
"""
AI記事自動生成エンジン (GitHub Pages版)
Claude APIを使用してアフィリエイト記事を自動生成
"""

import os
import anthropic
from datetime import datetime
from typing import Dict, List, Optional
import json


class ArticleGenerator:
    """Claude APIを使用した記事生成エンジン"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"

    def generate_article(
        self,
        topic: str,
        keywords: List[str],
        category: str = "AI",
        target_length: int = 3000,
        affiliate_products: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        記事を生成する

        Args:
            topic: 記事のトピック
            keywords: SEOキーワードリスト
            category: カテゴリー
            target_length: 目標文字数
            affiliate_products: アフィリエイト商品情報

        Returns:
            {
                "title": "記事タイトル",
                "content": "記事本文（Markdown形式）",
                "excerpt": "要約",
                "tags": ["タグ1", "タグ2"],
                "meta_description": "メタディスクリプション"
            }
        """

        # システムプロンプト
        system_prompt = self._build_system_prompt()

        # ユーザープロンプト
        user_prompt = self._build_user_prompt(
            topic=topic,
            keywords=keywords,
            category=category,
            target_length=target_length,
            affiliate_products=affiliate_products
        )

        # Claude APIコール（プロンプトキャッシュ利用）
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        # レスポンス解析
        result = self._parse_response(response.content[0].text)

        return result

    def _build_system_prompt(self) -> str:
        """システムプロンプトを構築"""
        return """あなたは優秀なSEOライター兼アフィリエイトマーケターです。

# あなたの役割
- 読者に価値を提供する高品質な記事を作成
- SEOを意識した構成とキーワード配置
- 自然な形でアフィリエイトリンクを組み込む
- 読みやすく、信頼性の高いコンテンツ

# 記事作成のルール
1. **タイトル**: 魅力的で検索されやすい（30-40文字）
2. **導入部**: 読者の興味を引く、問題提起
3. **本文**: 論理的な構成、見出しで整理
4. **結論**: 要点のまとめ、行動喚起
5. **SEO**: キーワードを自然に配置（密度2-3%）
6. **アフィリエイト**: 押し売り感のない自然な紹介

# 文体
- です・ます調
- 専門用語は適度に解説
- 親しみやすく、信頼できる
- 具体例・データを活用

# 禁止事項
- 誇大表現・虚偽情報
- 過度な商品推奨
- コピペ・盗用
- 差別的・攻撃的表現
"""

    def _build_user_prompt(
        self,
        topic: str,
        keywords: List[str],
        category: str,
        target_length: int,
        affiliate_products: Optional[List[Dict]]
    ) -> str:
        """ユーザープロンプトを構築"""

        prompt = f"""以下の条件で記事を作成してください：

## 記事情報
- **トピック**: {topic}
- **カテゴリー**: {category}
- **目標文字数**: {target_length}文字
- **SEOキーワード**: {', '.join(keywords)}

"""

        if affiliate_products:
            prompt += "## 紹介する商品\n"
            for i, product in enumerate(affiliate_products, 1):
                prompt += f"{i}. {product.get('name', '商品')} - {product.get('description', '')}\n"
            prompt += "\n"

        prompt += """## 出力形式
以下のJSON形式で出力してください：

```json
{
  "title": "記事タイトル（30-40文字）",
  "excerpt": "記事の要約（100-150文字）",
  "content": "記事本文（Markdown形式、目標文字数）",
  "tags": ["タグ1", "タグ2", "タグ3", "タグ4", "タグ5"],
  "meta_description": "SEO用メタディスクリプション（120-150文字）"
}
```

## 記事構成の例
1. 導入（問題提起・読者の悩み）
2. トピックの背景・重要性
3. 詳細解説（複数セクション）
4. 具体例・ケーススタディ
5. おすすめ商品紹介（アフィリエイト）
6. まとめ・行動喚起

## 注意事項
- Markdown形式で見出し（##, ###）を適切に使用
- リストや表を活用して読みやすく
- 商品紹介は自然に組み込む
- 読者のベネフィットを明確に

それでは記事を作成してください。
"""

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Claude APIのレスポンスを解析"""

        # JSONブロックを抽出
        import re
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)

        if json_match:
            json_str = json_match.group(1)
            try:
                result = json.loads(json_str)
                return result
            except json.JSONDecodeError:
                pass

        # フォールバック: 全体をJSONとしてパース
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # 最終フォールバック
            return {
                "title": "生成された記事",
                "content": response_text,
                "excerpt": response_text[:150],
                "tags": ["AI", "自動生成"],
                "meta_description": response_text[:120]
            }


def generate_sample_article():
    """サンプル記事を生成（テスト用）"""

    generator = ArticleGenerator()

    # テストトピック
    topic = "Claude 4.5の新機能と活用方法"
    keywords = ["Claude 4.5", "AI", "Claude API", "プログラミング", "自動化"]
    category = "AI"

    affiliate_products = [
        {
            "name": "プログラミング入門書",
            "description": "初心者向けPython学習本"
        }
    ]

    print("記事を生成中...")
    result = generator.generate_article(
        topic=topic,
        keywords=keywords,
        category=category,
        target_length=2000,
        affiliate_products=affiliate_products
    )

    print("\n=== 生成結果 ===")
    print(f"タイトル: {result['title']}")
    print(f"\n要約: {result['excerpt']}")
    print(f"\nタグ: {', '.join(result['tags'])}")
    print(f"\n本文（最初の500文字）:\n{result['content'][:500]}...")

    return result


if __name__ == "__main__":
    generate_sample_article()
