#!/usr/bin/env python3
"""
GitHub Pages自動投稿モジュール
Jekyll形式のMarkdownファイルを生成し、GitHub Pagesに自動デプロイ
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GitHubPagesPublisher:
    """GitHub Pages (Jekyll) への記事投稿クラス"""

    def __init__(self, posts_dir: str = "docs/_posts"):
        """
        初期化

        Args:
            posts_dir: Jekyll投稿ディレクトリパス
        """
        self.posts_dir = Path(posts_dir)
        self.posts_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, title: str) -> str:
        """
        タイトルをファイル名に変換

        Args:
            title: 記事タイトル

        Returns:
            サニタイズされたファイル名
        """
        # 記号を削除し、スペースをハイフンに
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '-', filename)
        return filename.lower().strip('-')

    def _create_jekyll_front_matter(
        self,
        title: str,
        date: datetime,
        categories: list[str] = None,
        tags: list[str] = None,
        excerpt: str = None
    ) -> str:
        """
        Jekyll Front Matterを生成

        Args:
            title: 記事タイトル
            date: 投稿日時
            categories: カテゴリーリスト
            tags: タグリスト
            excerpt: 記事要約

        Returns:
            Front Matter文字列
        """
        front_matter = [
            "---",
            f"layout: post",
            f"title: \"{title}\"",
            f"date: {date.strftime('%Y-%m-%d %H:%M:%S %z')}",
        ]

        if categories:
            front_matter.append(f"categories: {' '.join(categories)}")

        if tags:
            front_matter.append(f"tags: {' '.join(tags)}")

        if excerpt:
            front_matter.append(f"excerpt: \"{excerpt}\"")

        front_matter.append("---")
        front_matter.append("")  # 空行

        return "\n".join(front_matter)

    def publish_article(
        self,
        title: str,
        content: str,
        categories: list[str] = None,
        tags: list[str] = None,
        date: Optional[datetime] = None,
        excerpt: str = None
    ) -> Dict[str, any]:
        """
        記事をGitHub Pagesに投稿

        Args:
            title: 記事タイトル
            content: 記事本文（Markdown）
            categories: カテゴリーリスト
            tags: タグリスト
            date: 投稿日時（Noneの場合は現在時刻）
            excerpt: 記事要約

        Returns:
            投稿結果情報
        """
        if date is None:
            date = datetime.now()

        # Jekyll形式のファイル名: YYYY-MM-DD-title.md
        filename = f"{date.strftime('%Y-%m-%d')}-{self._sanitize_filename(title)}.md"
        filepath = self.posts_dir / filename

        # Front Matterを生成
        front_matter = self._create_jekyll_front_matter(
            title=title,
            date=date,
            categories=categories or [],
            tags=tags or [],
            excerpt=excerpt
        )

        # 完全な記事を生成
        full_content = f"{front_matter}\n{content}\n"

        # ファイルに書き込み
        try:
            filepath.write_text(full_content, encoding='utf-8')
            logger.info(f"記事を作成しました: {filepath}")

            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "url": f"/{date.strftime('%Y/%m/%d')}/{self._sanitize_filename(title)}.html",
                "message": "記事ファイルを生成しました。Git push後にGitHub Pagesで公開されます。"
            }

        except Exception as e:
            logger.error(f"記事の作成に失敗しました: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def list_articles(self) -> list[Dict[str, str]]:
        """
        投稿済み記事の一覧を取得

        Returns:
            記事情報のリスト
        """
        articles = []

        for filepath in sorted(self.posts_dir.glob("*.md"), reverse=True):
            if filepath.name == ".gitkeep":
                continue

            # ファイル名から日付とタイトルを抽出
            match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md', filepath.name)
            if match:
                date_str, title_slug = match.groups()
                articles.append({
                    "date": date_str,
                    "title_slug": title_slug,
                    "filepath": str(filepath),
                    "filename": filepath.name
                })

        return articles


def test_publisher():
    """テスト用関数"""
    publisher = GitHubPagesPublisher()

    # サンプル記事を投稿
    result = publisher.publish_article(
        title="AIアフィリエイト自動化システムのテスト投稿",
        content="""
# はじめに

これはGitHub Pages自動投稿のテスト記事です。

## 特徴

- 完全自動生成
- Jekyll対応
- SEO最適化済み

## まとめ

AI技術により24時間自動でコンテンツを生成・投稿できます。

[Amazonで関連商品を見る](https://amazon.co.jp/?tag=your-affiliate-id)
""",
        categories=["AI", "Technology"],
        tags=["自動化", "アフィリエイト", "Claude"],
        excerpt="GitHub Pages自動投稿システムのテスト記事です。"
    )

    print("投稿結果:", result)

    # 記事一覧を表示
    articles = publisher.list_articles()
    print(f"\n投稿済み記事数: {len(articles)}")
    for article in articles[:5]:
        print(f"  - {article['date']}: {article['title_slug']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_publisher()
