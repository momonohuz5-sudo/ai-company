"""note自動投稿モジュール

Note Client 2を使った記事投稿機能
⚠️ 非公式ライブラリのため、アカウント停止リスクあり
"""

import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .config import Config

# Note Client 2は条件付きインポート
try:
    from NoteClient2 import NoteClient2
    NOTE_CLIENT_AVAILABLE = True
except ImportError:
    NOTE_CLIENT_AVAILABLE = False
    logging.warning("NoteClient2 is not installed. Auto-posting is disabled.")


class NotePublisher:
    """note記事投稿クラス"""

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        user_urlname: Optional[str] = None,
    ):
        """初期化

        Args:
            email: noteログインメールアドレス
            password: noteログインパスワード
            user_urlname: noteユーザーID（プロフィールURLの末尾）
        """
        if not NOTE_CLIENT_AVAILABLE:
            raise ImportError(
                "noteclient2 is not installed. "
                "Install with: pip install noteclient2"
            )

        self.email = email or Config.NOTE_EMAIL
        self.password = password or Config.NOTE_PASSWORD
        self.user_urlname = user_urlname or Config.NOTE_USER_URL_ID

        if not all([self.email, self.password, self.user_urlname]):
            raise ValueError(
                "note credentials are required. "
                "Set NOTE_EMAIL, NOTE_PASSWORD, NOTE_USER_URL_ID in .env"
            )

        self.client = None
        self.logger = logging.getLogger(__name__)

    def login(self) -> bool:
        """noteにログイン

        Returns:
            bool: ログイン成功時True
        """
        try:
            self.logger.info("Logging in to note...")
            self.client = NoteClient2(
                email=self.email,
                password=self.password,
                user_urlname=self.user_urlname
            )
            self.logger.info("✓ Successfully logged in to note")
            return True

        except Exception as e:
            self.logger.error(f"✗ Failed to login: {e}")
            return False

    def publish_article(
        self,
        title: str,
        content: str,
        price: Optional[int] = None,
        images: Optional[List[Path]] = None,
        hashtags: Optional[List[str]] = None,
        magazine_id: Optional[str] = None,
        publish_at: Optional[datetime] = None,
    ) -> Dict[str, any]:
        """記事を投稿

        Args:
            title: 記事タイトル
            content: 記事本文（Markdown）
            price: 有料記事の場合の価格（円）。Noneで無料
            images: 画像ファイルパスのリスト
            hashtags: ハッシュタグのリスト
            magazine_id: マガジンID
            publish_at: 予約投稿日時（Noneで即座投稿）

        Returns:
            Dict: {
                "success": bool,
                "url": str or None,
                "note_id": str or None,
                "error": str or None,
            }
        """
        if self.client is None:
            if not self.login():
                return {"success": False, "error": "Login failed"}

        try:
            self.logger.info(f"Publishing article: {title}")

            # 価格設定（デフォルトは環境変数から）
            if price is None:
                price = Config.NOTE_ARTICLE_PRICE

            # 画像アップロード
            uploaded_images = []
            if images:
                self.logger.info(f"Uploading {len(images)} images...")
                for img_path in images:
                    try:
                        img_url = self.client.upload_image(str(img_path))
                        uploaded_images.append(img_url)
                        self.logger.info(f"✓ Uploaded: {img_path.name}")
                    except Exception as e:
                        self.logger.warning(f"✗ Failed to upload {img_path}: {e}")

            # 本文に画像を埋め込み
            if uploaded_images:
                content += "\n\n---\n\n"
                for img_url in uploaded_images:
                    content += f"![image]({img_url})\n\n"

            # ハッシュタグ追加
            if hashtags:
                content += "\n\n---\n\n"
                content += " ".join([f"#{tag}" for tag in hashtags])

            # 一時ファイルにMarkdownを保存
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_md_path = f.name

            try:
                # 記事投稿
                self.logger.info("Posting article to note...")

                # Note Client 2のAPIに従って投稿
                result = self.client.publish(
                    title=title,
                    md_file_path=temp_md_path,
                    eyecatch_path=str(images[0]) if images else None,
                    hashtags=hashtags,
                    price=price if price > 0 else 0,
                    magazine_key=None,  # マガジンは後で設定
                    is_publish=True,  # 即座に公開
                )

                self.logger.info(f"✓ Successfully published: {result.get('url')}")
            finally:
                # 一時ファイルを削除
                import os
                os.unlink(temp_md_path)

            return {
                "success": True,
                "url": result.get("url"),
                "note_id": result.get("id"),
                "error": None,
            }

        except Exception as e:
            self.logger.error(f"✗ Failed to publish article: {e}")
            return {
                "success": False,
                "url": None,
                "note_id": None,
                "error": str(e),
            }

    def add_to_magazine(self, note_id: str, magazine_id: Optional[str] = None) -> bool:
        """記事をマガジンに追加

        Args:
            note_id: 記事ID
            magazine_id: マガジンID

        Returns:
            bool: 成功時True
        """
        if self.client is None:
            if not self.login():
                return False

        try:
            magazine_id = magazine_id or Config.NOTE_MAGAZINE_ID
            if not magazine_id:
                self.logger.warning("Magazine ID is not set")
                return False

            self.logger.info(f"Adding article {note_id} to magazine {magazine_id}")
            self.client.add_to_magazine(note_id, magazine_id)
            self.logger.info("✓ Successfully added to magazine")
            return True

        except Exception as e:
            self.logger.error(f"✗ Failed to add to magazine: {e}")
            return False

    def export_as_markdown(
        self,
        title: str,
        content: str,
        output_path: Path,
        metadata: Optional[Dict] = None,
    ) -> Path:
        """記事をMarkdownファイルとして保存（手動投稿用フォールバック）

        Args:
            title: 記事タイトル
            content: 記事本文
            output_path: 保存先パス
            metadata: メタデータ（辞書）

        Returns:
            Path: 保存されたファイルパス
        """
        markdown = f"# {title}\n\n"

        if metadata:
            markdown += "---\n"
            for key, value in metadata.items():
                markdown += f"**{key}**: {value}\n"
            markdown += "---\n\n"

        markdown += content

        output_path.write_text(markdown, encoding="utf-8")
        self.logger.info(f"✓ Exported to: {output_path}")

        return output_path


class MockNotePublisher(NotePublisher):
    """テスト用モックパブリッシャー

    実際にnoteに投稿せず、ログ出力とファイル保存のみ行う
    """

    def __init__(self, *args, **kwargs):
        """初期化（Note Client 2は不要）"""
        self.logger = logging.getLogger(__name__)
        self.email = Config.NOTE_EMAIL
        self.password = "***"
        self.user_urlname = Config.NOTE_USER_URL_ID

    def login(self) -> bool:
        """モックログイン"""
        self.logger.info("[MOCK] Logged in to note")
        return True

    def publish_article(self, title: str, content: str, **kwargs) -> Dict[str, any]:
        """モック投稿"""
        self.logger.info(f"[MOCK] Publishing article: {title}")
        self.logger.info(f"[MOCK] Price: {kwargs.get('price', 0)}円")
        self.logger.info(f"[MOCK] Content length: {len(content)}字")

        # ファイル保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Config.BACKUP_DIR / f"{timestamp}_{title[:30]}.md"
        self.export_as_markdown(title, content, output_path)

        mock_url = f"https://note.com/{self.user_urlname}/n/mock{timestamp}"

        return {
            "success": True,
            "url": mock_url,
            "note_id": f"mock{timestamp}",
            "error": None,
        }

    def add_to_magazine(self, note_id: str, magazine_id: Optional[str] = None) -> bool:
        """モックマガジン追加"""
        self.logger.info(f"[MOCK] Added article {note_id} to magazine {magazine_id}")
        return True
