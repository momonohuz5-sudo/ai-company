#!/usr/bin/env python3
"""
GitHub Pages 記事投稿モジュール
生成された記事をJekyll形式で保存
"""

import os
from datetime import datetime
from typing import Dict, List
import re


class GitHubPagesPublisher:
    """Jekyll形式での記事投稿"""

    def __init__(self, posts_dir: str = "./docs/_posts"):
        self.posts_dir = posts_dir
        os.makedirs(self.posts_dir, exist_ok=True)

    def publish_article(
        self,
        article: Dict[str, str],
        categories: List[str] = None,
        publish_date: datetime = None,
        skip_publish: bool = False
    ) -> str:
        """
        記事を投稿（Jekyllファイルとして保存）

        Args:
            article: 記事データ {title, content, excerpt, tags, meta_description}
            categories: カテゴリーリスト
            publish_date: 公開日時（Noneの場合は現在時刻）
            skip_publish: Trueの場合は実際には保存しない（テスト用）

        Returns:
            保存したファイルパス
        """

        if publish_date is None:
            publish_date = datetime.now()

        # ファイル名生成
        filename = self._generate_filename(article["title"], publish_date)
        filepath = os.path.join(self.posts_dir, filename)

        # Jekyllフロントマター + 本文
        content = self._build_jekyll_post(
            article=article,
            categories=categories or ["AI"],
            publish_date=publish_date
        )

        # ファイル保存
        if not skip_publish:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 記事を保存しました: {filepath}")
        else:
            print(f"🔍 [テストモード] 保存をスキップ: {filepath}")

        return filepath

    def _generate_filename(self, title: str, publish_date: datetime) -> str:
        """Jekyll形式のファイル名を生成: YYYY-MM-DD-title-slug.md"""

        # タイトルをslug化
        slug = self._slugify(title)

        # 日付フォーマット
        date_str = publish_date.strftime("%Y-%m-%d")

        return f"{date_str}-{slug}.md"

    def _slugify(self, text: str) -> str:
        """タイトルをURLフレンドリーなslugに変換"""

        # 日本語を含む場合はローマ字化は行わず、記号のみ処理
        text = text.lower()

        # 特殊文字を削除
        text = re.sub(r'[^\w\s぀-ゟ゠-ヿ一-鿿-]', '', text)

        # スペースをハイフンに
        text = re.sub(r'[\s_]+', '-', text)

        # 連続ハイフンを1つに
        text = re.sub(r'-+', '-', text)

        # 前後のハイフンを削除
        text = text.strip('-')

        # 長すぎる場合は切り詰め（50文字）
        if len(text) > 50:
            text = text[:50].rstrip('-')

        return text or "article"

    def _build_jekyll_post(
        self,
        article: Dict[str, str],
        categories: List[str],
        publish_date: datetime
    ) -> str:
        """Jekyll投稿ファイルの内容を構築"""

        # フロントマター
        frontmatter = "---\n"
        frontmatter += "layout: post\n"
        frontmatter += f"title: \"{article['title']}\"\n"
        frontmatter += f"date: {publish_date.strftime('%Y-%m-%d %H:%M:%S')} +0900\n"
        frontmatter += f"categories: {categories}\n"

        if "tags" in article and article["tags"]:
            tags_str = str(article["tags"]).replace("'", "")
            frontmatter += f"tags: {tags_str}\n"

        if "excerpt" in article and article["excerpt"]:
            # 改行を削除
            excerpt = article["excerpt"].replace("\n", " ")
            frontmatter += f"excerpt: \"{excerpt}\"\n"

        frontmatter += "---\n\n"

        # 本文
        content = article["content"]

        # アフィリエイト開示（記事末尾に追加）
        affiliate_disclosure = """

---

<div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 30px;">
<p><strong>📢 アフィリエイト開示</strong></p>
<p>本記事内のリンクから商品を購入いただいた場合、当サイトに紹介手数料が入る場合があります。これにより、サイト運営を継続し、より良いコンテンツを提供できます。</p>
</div>
"""

        full_content = frontmatter + content + affiliate_disclosure

        return full_content

    def list_published_articles(self, limit: int = 10) -> List[str]:
        """投稿済み記事のリストを取得"""

        files = []
        if os.path.exists(self.posts_dir):
            all_files = os.listdir(self.posts_dir)
            md_files = [f for f in all_files if f.endswith('.md')]
            md_files.sort(reverse=True)  # 新しい順
            files = md_files[:limit]

        return files


def test_publisher():
    """テスト実行"""

    publisher = GitHubPagesPublisher()

    # サンプル記事
    sample_article = {
        "title": "テスト記事: Claude 4.5 完全ガイド",
        "excerpt": "Claude 4.5の新機能と活用方法を徹底解説します。",
        "content": """
# Claude 4.5 完全ガイド

Claude 4.5は、Anthropicが開発した最新のAI言語モデルです。

## 主な特徴

1. **高性能な言語理解**
2. **長いコンテキスト対応**
3. **プロンプトキャッシング**

## 活用方法

Claude 4.5は様々な用途で活用できます。

### プログラミング支援

コード生成、デバッグ、リファクタリングに最適です。

### コンテンツ制作

ブログ記事、マーケティングコピー、技術文書の作成をサポート。

## まとめ

Claude 4.5を活用することで、業務効率を大幅に向上できます。
""",
        "tags": ["Claude", "AI", "プログラミング", "自動化"],
        "meta_description": "Claude 4.5の新機能と実用的な活用方法を詳しく解説。"
    }

    # 投稿テスト
    filepath = publisher.publish_article(
        article=sample_article,
        categories=["AI", "テクノロジー"],
        skip_publish=False
    )

    print(f"\n投稿完了: {filepath}")

    # 記事一覧
    print("\n=== 投稿済み記事 ===")
    articles = publisher.list_published_articles()
    for article in articles:
        print(f"- {article}")


if __name__ == "__main__":
    test_publisher()
