"""
WordPress自動投稿モジュール
生成された記事をWordPressに自動投稿
"""
import os
import json
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests


class WordPressPublisher:
    """WordPressへの記事投稿を管理するクラス"""

    def __init__(
        self,
        wp_url: str = None,
        username: str = None,
        app_password: str = None
    ):
        """
        WordPressサイトへの接続設定

        Args:
            wp_url: WordPressサイトのURL
            username: WordPressユーザー名
            app_password: アプリケーションパスワード
        """
        self.wp_url = (wp_url or os.getenv('WORDPRESS_URL', '')).rstrip('/')
        self.username = username or os.getenv('WORDPRESS_USERNAME', '')
        self.app_password = app_password or os.getenv('WORDPRESS_APP_PASSWORD', '')

        if not all([self.wp_url, self.username, self.app_password]):
            raise ValueError("WordPress接続情報が不足しています")

        # REST API エンドポイント
        self.api_base = f"{self.wp_url}/wp-json/wp/v2"

        # 認証ヘッダー
        credentials = f"{self.username}:{self.app_password}"
        token = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }

    def test_connection(self) -> bool:
        """WordPress接続テスト"""
        try:
            response = requests.get(
                f"{self.api_base}/users/me",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                user_data = response.json()
                print(f"WordPress接続成功: {user_data.get('name')}")
                return True
            else:
                print(f"WordPress接続失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"WordPress接続エラー: {e}")
            return False

    def create_post(
        self,
        title: str,
        content: str,
        status: str = 'draft',
        categories: List[int] = None,
        tags: List[int] = None,
        featured_media: int = None,
        excerpt: str = None,
        meta: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        WordPress投稿を作成

        Args:
            title: 記事タイトル
            content: 記事本文（HTML or Markdown）
            status: 投稿ステータス ('draft', 'publish', 'future')
            categories: カテゴリIDリスト
            tags: タグIDリスト
            featured_media: アイキャッチ画像ID
            excerpt: 抜粋
            meta: カスタムフィールド

        Returns:
            作成された投稿データ
        """
        post_data = {
            'title': title,
            'content': content,
            'status': status,
        }

        if excerpt:
            post_data['excerpt'] = excerpt

        if categories:
            post_data['categories'] = categories

        if tags:
            post_data['tags'] = tags

        if featured_media:
            post_data['featured_media'] = featured_media

        if meta:
            post_data['meta'] = meta

        try:
            response = requests.post(
                f"{self.api_base}/posts",
                headers=self.headers,
                json=post_data,
                timeout=30
            )

            if response.status_code == 201:
                post = response.json()
                print(f"投稿作成成功: {post.get('id')} - {post.get('link')}")
                return post
            else:
                print(f"投稿作成失敗: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"投稿作成エラー: {e}")
            return None

    def update_post(
        self,
        post_id: int,
        title: str = None,
        content: str = None,
        status: str = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """既存の投稿を更新"""
        update_data = {}

        if title:
            update_data['title'] = title
        if content:
            update_data['content'] = content
        if status:
            update_data['status'] = status

        update_data.update(kwargs)

        try:
            response = requests.post(
                f"{self.api_base}/posts/{post_id}",
                headers=self.headers,
                json=update_data,
                timeout=30
            )

            if response.status_code == 200:
                post = response.json()
                print(f"投稿更新成功: {post_id}")
                return post
            else:
                print(f"投稿更新失敗: {response.status_code}")
                return None

        except Exception as e:
            print(f"投稿更新エラー: {e}")
            return None

    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """カテゴリを取得または作成"""
        try:
            # 既存カテゴリを検索
            response = requests.get(
                f"{self.api_base}/categories",
                headers=self.headers,
                params={'search': category_name},
                timeout=10
            )

            if response.status_code == 200:
                categories = response.json()
                if categories:
                    return categories[0]['id']

            # 新規作成
            response = requests.post(
                f"{self.api_base}/categories",
                headers=self.headers,
                json={'name': category_name},
                timeout=10
            )

            if response.status_code == 201:
                return response.json()['id']

        except Exception as e:
            print(f"カテゴリ作成エラー: {e}")

        return None

    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """タグを取得または作成"""
        try:
            # 既存タグを検索
            response = requests.get(
                f"{self.api_base}/tags",
                headers=self.headers,
                params={'search': tag_name},
                timeout=10
            )

            if response.status_code == 200:
                tags = response.json()
                if tags:
                    return tags[0]['id']

            # 新規作成
            response = requests.post(
                f"{self.api_base}/tags",
                headers=self.headers,
                json={'name': tag_name},
                timeout=10
            )

            if response.status_code == 201:
                return response.json()['id']

        except Exception as e:
            print(f"タグ作成エラー: {e}")

        return None

    def publish_article(
        self,
        article_data: Dict[str, Any],
        auto_publish: bool = False,
        category_name: str = 'アフィリエイト'
    ) -> Optional[Dict[str, Any]]:
        """
        記事データからWordPress投稿を作成

        Args:
            article_data: 記事データ（article_generator.pyの出力）
            auto_publish: 即時公開するか（Falseの場合は下書き）
            category_name: カテゴリ名

        Returns:
            作成された投稿データ
        """
        title = article_data.get('title', '')
        content = article_data.get('content', '')
        keyword = article_data.get('keyword', '')
        seo_metadata = article_data.get('seo_metadata', {})

        # カテゴリ・タグを取得/作成
        category_id = self.get_or_create_category(category_name)
        tag_id = self.get_or_create_tag(keyword)

        categories = [category_id] if category_id else []
        tags = [tag_id] if tag_id else []

        # 投稿作成
        status = 'publish' if auto_publish else 'draft'

        post = self.create_post(
            title=title,
            content=content,
            status=status,
            categories=categories,
            tags=tags,
            excerpt=seo_metadata.get('meta_description', '')
        )

        if post:
            # 投稿記録を保存
            self._save_publish_log({
                'post_id': post.get('id'),
                'post_url': post.get('link'),
                'title': title,
                'keyword': keyword,
                'status': status,
                'published_at': datetime.now().isoformat()
            })

        return post

    def _save_publish_log(self, log_data: Dict[str, Any]):
        """投稿ログを保存"""
        log_dir = os.path.join(os.path.dirname(__file__), 'publish_logs')
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, 'publish_history.json')

        # 既存ログ読み込み
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        # 新規ログ追加
        logs.append(log_data)

        # 保存
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def batch_publish_articles(
        self,
        articles: List[Dict[str, Any]],
        auto_publish: bool = False
    ) -> List[Dict[str, Any]]:
        """複数記事を一括投稿"""
        results = []

        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}] 投稿中: {article.get('title', '')}")

            try:
                post = self.publish_article(article, auto_publish=auto_publish)
                if post:
                    results.append(post)
                    print(f"✓ 投稿成功: {post.get('link')}")
            except Exception as e:
                print(f"✗ 投稿失敗: {e}")

        print(f"\n一括投稿完了: {len(results)}/{len(articles)} 件")
        return results


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    # 接続テスト
    publisher = WordPressPublisher()

    if publisher.test_connection():
        print("\nWordPress接続テスト: 成功")
    else:
        print("\nWordPress接続テスト: 失敗")
        print("環境変数を確認してください:")
        print("- WORDPRESS_URL")
        print("- WORDPRESS_USERNAME")
        print("- WORDPRESS_APP_PASSWORD")
