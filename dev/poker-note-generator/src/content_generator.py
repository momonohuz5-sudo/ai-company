"""Claude APIを使った記事生成エンジン"""

import anthropic
from pathlib import Path
from typing import Dict, Optional, Literal
import json
from datetime import datetime

from .config import Config


class ContentGenerator:
    """記事生成クラス"""

    def __init__(self, api_key: Optional[str] = None):
        """初期化

        Args:
            api_key: Anthropic APIキー（省略時は環境変数から取得）
        """
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = anthropic.Anthropic(api_key=self.api_key)

        # プロンプト読み込み
        self.system_prompt = self._load_prompt("system_prompt.txt")
        self.templates = {
            1: self._load_prompt("beginner_template.txt"),
            2: self._load_prompt("intermediate_template.txt"),
            3: self._load_prompt("intermediate_template.txt"),
            4: self._load_prompt("advanced_template.txt"),
            5: self._load_prompt("advanced_template.txt"),
        }

    def _load_prompt(self, filename: str) -> str:
        """プロンプトファイルを読み込み

        Args:
            filename: プロンプトファイル名

        Returns:
            str: プロンプト内容
        """
        path = Config.PROMPTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")

        return path.read_text(encoding="utf-8")

    def generate_article(
        self,
        topic: str,
        difficulty: int = 2,
        specific_scenario: Optional[str] = None,
        include_chart: bool = True,
    ) -> Dict[str, any]:
        """記事を生成

        Args:
            topic: トピック（例: "プリフロップレンジの基本"）
            difficulty: 難易度 1-5（★の数）
            specific_scenario: 具体的なシナリオ（省略可）
            include_chart: レンジチャートを含めるか

        Returns:
            Dict: {
                "title": str,
                "content": str,  # Markdown
                "difficulty": int,
                "topic": str,
                "chart_data": Dict or None,
                "metadata": Dict
            }
        """
        # テンプレート選択
        template = self.templates.get(difficulty, self.templates[2])

        # ユーザープロンプト構築
        user_prompt = f"""
以下の条件でポーカー戦略記事を執筆してください。

## 記事テンプレート
{template}

## トピック
{topic}
"""

        if specific_scenario:
            user_prompt += f"\n## 具体的なシナリオ\n{specific_scenario}\n"

        if include_chart:
            user_prompt += """
## レンジチャート
記事内に13×13レンジチャートを含めてください。
チャートのデータは以下のJSON形式で提供してください：

```json
{{
  "chart_title": "チャートのタイトル",
  "range_data": {{
    "AA": "allin",
    "KK": "raise",
    "AKs": "raise",
    ...
  }}
}}
```

アクション: fold, call, raise, allin, check
"""

        user_prompt += """
## 出力フォーマット
以下の形式で出力してください：

---TITLE---
記事タイトル（60文字以内）

---CONTENT---
記事本文（Markdown形式）

---CHART_DATA---
```json
{レンジチャートデータ（あれば）}
```
"""

        # Claude API呼び出し（Prompt Caching使用）
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4000,
                system=[
                    {
                        "type": "text",
                        "text": self.system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
            )

            response_text = message.content[0].text

            # レスポンスをパース
            result = self._parse_response(response_text)
            result["difficulty"] = difficulty
            result["topic"] = topic
            result["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "model": "claude-sonnet-4-5",
                "tokens": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens,
                    "cache_read": getattr(message.usage, "cache_read_input_tokens", 0),
                    "cache_creation": getattr(message.usage, "cache_creation_input_tokens", 0),
                },
            }

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to generate article: {e}")

    def _parse_response(self, response: str) -> Dict[str, any]:
        """Claude APIのレスポンスをパース

        Args:
            response: APIレスポンステキスト

        Returns:
            Dict: パース結果
        """
        result = {
            "title": "",
            "content": "",
            "chart_data": None,
        }

        # タイトル抽出
        if "---TITLE---" in response:
            parts = response.split("---TITLE---")
            if len(parts) > 1:
                title_part = parts[1].split("---CONTENT---")[0].strip()
                result["title"] = title_part

        # コンテンツ抽出
        if "---CONTENT---" in response:
            parts = response.split("---CONTENT---")
            if len(parts) > 1:
                content_part = parts[1].split("---CHART_DATA---")[0].strip()
                result["content"] = content_part

        # チャートデータ抽出
        if "---CHART_DATA---" in response:
            try:
                chart_part = response.split("---CHART_DATA---")[1].strip()
                # JSONブロック抽出
                if "```json" in chart_part:
                    json_str = chart_part.split("```json")[1].split("```")[0].strip()
                    result["chart_data"] = json.loads(json_str)
            except Exception as e:
                print(f"Warning: Failed to parse chart data: {e}")

        return result

    def save_article(self, article_data: Dict, output_dir: Path = None) -> Path:
        """記事をファイルに保存

        Args:
            article_data: generate_article()の戻り値
            output_dir: 保存先ディレクトリ

        Returns:
            Path: 保存されたファイルのパス
        """
        if output_dir is None:
            output_dir = Config.ARTICLES_DIR

        # ファイル名生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        difficulty_stars = "★" * article_data["difficulty"]
        filename = f"{timestamp}_{difficulty_stars}_{article_data['topic'][:20]}.md"
        # ファイル名から不正な文字を除去
        filename = "".join(c for c in filename if c.isalnum() or c in "._-★")
        filepath = output_dir / filename

        # Markdown形式で保存
        content = f"# {article_data['title']}\n\n"
        content += f"**難易度**: {difficulty_stars}\n\n"
        content += f"**トピック**: {article_data['topic']}\n\n"
        content += "---\n\n"
        content += article_data["content"]

        # メタデータも追記
        content += "\n\n---\n\n"
        content += f"**生成日時**: {article_data['metadata']['generated_at']}\n"
        content += f"**モデル**: {article_data['metadata']['model']}\n"

        filepath.write_text(content, encoding="utf-8")

        return filepath
