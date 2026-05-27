# SFW Image Generation System

AI Company開発部門 - ComfyUI Cloud統合システム

## 概要

このシステムは**SFW（Safe For Work）のみ**の画像生成を目的とした、ComfyUI Cloudの統合ソリューションです。

### 主要機能

1. **ComfyUI統合** (`comfyui_integration.py`)
   - ComfyUI Cloud APIクライアント
   - 自動NSFW除外フィルター
   - ワークフロー管理
   - デフォルトSFWワークフロー（風景、製品、イラスト、UI、マーケティング）

2. **プロンプト管理** (`prompt_manager.py`)
   - カテゴリ別テンプレート管理
   - プロンプト生成履歴
   - 検索機能
   - デフォルトSFWテンプレート

3. **画像整理システム** (`image_organizer.py`)
   - メタデータ管理
   - カテゴリ別整理
   - バッチ処理
   - 統計情報

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集してComfyUI APIキーを設定：

```bash
COMFYUI_API_KEY=your_actual_api_key
```

### 3. 初期化

```bash
python sfw_image_generator.py init
```

これにより以下が作成されます：
- デフォルトワークフロー（5種類）
- デフォルトプロンプトテンプレート（7種類）

## 使い方

### 基本的な画像生成

```bash
python sfw_image_generator.py generate "beautiful mountain landscape at sunset"
```

### テンプレートを使用

```bash
python sfw_image_generator.py generate \
  --template scenic_landscape \
  "mountain valley" "sunset" "clear sky"
```

### ワークフローを使用

```bash
python sfw_image_generator.py generate \
  --workflow landscape \
  "beautiful forest scene"
```

### カスタムパラメータ

```bash
python sfw_image_generator.py generate \
  "modern architecture building" \
  --width 1920 \
  --height 1080 \
  --steps 40 \
  --cfg-scale 8.0 \
  --category architecture \
  --tags building modern design
```

### バッチ生成

`prompts.json`を作成：

```json
[
  "beautiful sunset over ocean",
  "modern office interior design",
  "healthy food photography"
]
```

実行：

```bash
python sfw_image_generator.py batch prompts.json --category marketing
```

### テンプレート一覧

```bash
python sfw_image_generator.py templates
```

### ワークフロー一覧

```bash
python sfw_image_generator.py workflows
```

### 統計情報

```bash
python sfw_image_generator.py stats
```

### 画像一覧

```bash
python sfw_image_generator.py list --limit 20
python sfw_image_generator.py list --category landscape
python sfw_image_generator.py list --status completed
```

## デフォルトワークフロー

| ワークフロー | 用途 | デフォルトサイズ |
|---|---|---|
| `landscape` | 風景・自然 | 1920x1080 |
| `product_design` | 製品デザイン | 1024x1024 |
| `illustration` | イラスト・アート | 1024x1536 |
| `ui_mockup` | UI/UXデザイン | 1440x900 |
| `marketing_visual` | マーケティング素材 | 1200x630 |

## デフォルトテンプレート

| テンプレート | カテゴリ | 変数 |
|---|---|---|
| `scenic_landscape` | landscape | location, time_of_day, weather |
| `product_showcase` | product | product, background |
| `artistic_illustration` | illustration | subject, style, color_scheme |
| `modern_architecture` | architecture | building_type, material, environment |
| `food_photography` | food | dish, presentation |
| `tech_visualization` | technology | technology, color_theme |
| `abstract_art` | abstract | pattern, color_palette, mood |

## ディレクトリ構造

```
dev/
├── comfyui_integration.py    # ComfyUI API統合
├── prompt_manager.py          # プロンプト管理
├── image_organizer.py         # 画像整理
├── sfw_image_generator.py     # メインCLI
├── requirements.txt           # 依存関係
├── .env.example              # 環境変数テンプレート
├── workflows/                # ワークフロー定義
├── prompts/                  # プロンプトテンプレート
└── generated_images/         # 生成画像
    ├── images/
    │   ├── landscape/
    │   ├── product/
    │   └── ...
    └── metadata.json
```

## Python APIとして使用

```python
from sfw_image_generator import SFWImageGenerator

gen = SFWImageGenerator()

# シンプルな生成
result = gen.generate("beautiful sunset landscape")

# テンプレート使用
result = gen.generate(
    prompt="",
    template="scenic_landscape",
    location="beach",
    time_of_day="golden hour",
    weather="partly cloudy"
)

# ワークフロー使用
result = gen.generate(
    prompt="modern smartphone",
    workflow="product_design",
    category="product"
)

# 統計確認
print(gen.show_stats())
```

## 安全性機能

### 自動NSFWフィルタリング

すべてのプロンプトに自動的に以下が追加されます：

**ポジティブ追加：**
- safe for work
- family friendly
- professional

**ネガティブプロンプト追加：**
- nsfw, nude, nudity, explicit
- adult content, sexual, provocative
- inappropriate, mature content
- 18+, r18

### カテゴリ制限

すべてのテンプレートとワークフローは以下のSFWカテゴリに限定：
- landscape（風景）
- portrait（ポートレート）
- product（製品）
- illustration（イラスト）
- architecture（建築）
- food（食品）
- nature（自然）
- technology（技術）
- art（アート）
- abstract（抽象）

## トラブルシューティング

### API接続エラー

```bash
# APIキーを確認
cat .env

# 接続テスト
python -c "from comfyui_integration import ComfyUIClient; print(ComfyUIClient().session.headers)"
```

### 生成失敗の確認

```bash
# 失敗したジョブを確認
python sfw_image_generator.py list --status failed

# クリーンアップ
python -c "from image_organizer import ImageOrganizer; print(ImageOrganizer().cleanup_failed())"
```

## ライセンス

AI Company内部使用のみ。商用利用時はComfyUI Cloudの利用規約を確認してください。

## サポート

問題が発生した場合：
1. `dev/CLAUDE.md`を確認
2. PMに連絡
3. GitHub Issueを作成

---

**重要:** このシステムはSFW（一般向け）コンテンツのみを対象としています。NSFWコンテンツの生成は設計上ブロックされています。
