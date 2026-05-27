#!/usr/bin/env python
"""NoteClient2のレスポンステスト"""

import logging
import tempfile
from NoteClient2 import NoteClient2
from src.config import Config

logging.basicConfig(level=logging.INFO)

# ログイン
print("ログイン中...")
client = NoteClient2(
    email=Config.NOTE_EMAIL,
    password=Config.NOTE_PASSWORD,
    user_urlname=Config.NOTE_USER_URLNAME,
)
print("✓ ログイン成功\n")

# テスト記事作成
test_content = """# テスト記事

これはNoteClient2のテスト投稿です。

## 内容

- テスト項目1
- テスト項目2
- テスト項目3

このテストが成功したら、自動投稿システムが動作しています！
"""

# 一時ファイルに保存
with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
    f.write(test_content)
    temp_path = f.name

print(f"一時ファイル: {temp_path}\n")

# 投稿
print("投稿中...")
result = client.publish(
    title="【テスト】自動投稿システム動作確認",
    md_file_path=temp_path,
    eyecatch_path=None,
    hashtags=["テスト"],
    price=0,
    magazine_key=None,
    is_publish=True,
)

print("\n✓ 投稿完了！\n")
print("=" * 60)
print("レスポンス内容:")
print("=" * 60)
print(f"Type: {type(result)}")
print(f"Content: {result}")
print("=" * 60)

# レスポンスの構造を解析
if isinstance(result, dict):
    print("\nキー一覧:")
    for key in result.keys():
        print(f"  - {key}: {result[key]}")

# 一時ファイル削除
import os
os.unlink(temp_path)

print("\n完了！")
