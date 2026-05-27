# ポーカー戦略noteマガジン自動生成システム

Claude APIを活用して、ポーカー戦略コンテンツを自動生成し、noteで月額マガジンとして配信するシステムです。

## 特徴

- 📅 **毎日1記事自動生成・投稿**（月30記事）
- 🎯 **全レベル対応**（初心者★ 〜 上級者★★★★★）
- 📊 **GTOwizardスタイル**のレンジチャート画像を自動生成
- 🏆 **大型トーナメントハンドレビュー**（月2-3回）
- 🤖 **Claude API (Sonnet 4.5)** + Prompt Caching

## システム構成

```
poker-note-generator/
├── src/                    # ソースコード
│   ├── content_generator.py    # Claude API記事生成
│   ├── range_chart_renderer.py # レンジチャート描画
│   ├── config.py               # 設定管理
│   └── ...
├── data/                   # データ
│   ├── prompts/               # プロンプトテンプレート
│   └── hand_histories/        # 大会ハンドデータ
├── output/                 # 出力
│   ├── articles/              # 生成記事（Markdown）
│   └── images/                # レンジチャート画像
└── main.py                 # メインエントリーポイント
```

## セットアップ

### 1. 環境構築

```bash
# Python 3.12.7推奨
python --version

# 依存パッケージインストール
pip install -r requirements.txt

# Playwright（Note Client 2用）
playwright install
```

### 2. 環境変数設定

```bash
# .envファイル作成
cp .env.example .env

# .envを編集
nano .env
```

必須の設定:
- `ANTHROPIC_API_KEY`: Claude APIキー

### 3. テスト実行

```bash
# レンジチャート描画テスト
python main.py test-chart

# 記事生成テスト（Claude API必要）
python main.py test-content

# ワークフロー統合テスト（モック投稿）
python main.py test-workflow

# バッチ生成テスト（週間記事5本）
python main.py test-batch

# 全テスト
python main.py all
```

### 4. スケジューラー起動

```bash
# モックモードで起動（実際には投稿しない）
python -m src.scheduler --mock

# 1回だけテスト実行
python -m src.scheduler --mock --once

# 本番モード（実際に投稿する）
python -m src.scheduler
```

## 使い方

### 記事生成

```python
from src.content_generator import ContentGenerator

generator = ContentGenerator()

# 記事生成
article = generator.generate_article(
    topic="プリフロップレンジの基本",
    difficulty=1,  # 1-5（★の数）
    specific_scenario="BTNからのオープンレイズ",
    include_chart=True
)

# 保存
filepath = generator.save_article(article)
print(f"記事を保存: {filepath}")
```

### レンジチャート生成

```python
from src.range_chart_renderer import RangeChartRenderer

renderer = RangeChartRenderer()

# チャートデータ
range_data = {
    "AA": "allin",
    "KK": "raise",
    "AKs": "raise",
    # ...
}

# 描画
chart_path = renderer.render_chart(
    range_data=range_data,
    title="UTG Open Range",
    output_path="range_chart.png"
)
```

## 開発ロードマップ

### ✅ Milestone 1: プロンプト設計とパイロット生成（完了）
- [x] プロジェクト構造構築
- [x] プロンプトテンプレート作成
- [x] Claude API統合
- [x] レンジチャート描画エンジン

### ✅ Milestone 2: 記事生成の自動化（完了）
- [x] 難易度別テンプレートエンジン
- [x] 統合ワークフロー実装
- [x] バッチ生成機能

### ✅ Milestone 3: Note Client 2統合（完了）
- [x] 自動投稿機能
- [x] マガジン管理
- [x] エラーハンドリング
- [x] モック実行モード

### ✅ Milestone 4: スケジューリング（完了）
- [x] 毎日自動実行（APScheduler）
- [x] 曜日別テーマローテーション
- [x] 難易度ローテーション管理

## コスト試算

| 項目 | 月額 |
|------|------|
| Claude API | $30-100 |
| noteプレミアム | ¥500 |
| ホスティング | $0-50 |
| **合計** | **¥5,000-15,000** |

損益分岐点: 13-38購読者

## ライセンス

Private - AI Company internal use only

## 開発者

AI Company - Dev Team
