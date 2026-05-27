## Quick Start Guide - 画像生成まで5分

### 前提条件

- Python 3.8以上
- ComfyUI（オプション: dry-runモードなら不要）

### ステップ1: セットアップ（1分）

```bash
cd dev/image-pipeline

# 依存関係インストール
pip install -r requirements.txt

# 設定ファイル作成
cp config/settings.example.yaml config/settings.yaml
```

### ステップ2: デモ実行（1分）

```bash
# Dry-runモードでデモ実行
python examples/demo_workflow.py
```

このコマンドで以下が自動的に行われます:
- ✅ 作品作成 (demo_work_001)
- ✅ プロンプトブロック作成 (quality, character, setting, lighting, camera)
- ✅ プライベートブロック参照作成
- ✅ シーン計画生成 (3シーン)
- ✅ ComfyUIワークフロー構築
- ✅ バッチ送信（dry-run）

### ステップ3: 実際の画像生成（ComfyUI必要）

#### 3-1. ComfyUIのインストールと起動

```bash
# ComfyUIをダウンロード（初回のみ）
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# ComfyUI起動
python main.py --listen 0.0.0.0
```

デフォルトで `http://localhost:8188` で起動します。

#### 3-2. 設定ファイル編集

`config/settings.yaml` を編集:

```yaml
comfyui:
  endpoint: "http://localhost:8188"  # ComfyUIのURL
  dry_run: false                     # ★ここをfalseに変更
```

#### 3-3. プライベートブロック編集（オプション）

より良い画像生成のため、プライベートブロックを編集:

`data/private/blocks/private_demo_001.json`:
```json
{
  "content": "detailed face, beautiful eyes, perfect anatomy",
  "tags": []
}
```

`data/private/blocks/negative_demo_001.json`:
```json
{
  "content": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
  "tags": []
}
```

#### 3-4. 実行

```bash
# 実際の画像生成
python examples/demo_workflow.py
```

ComfyUIのUIで生成進行状況が確認できます: `http://localhost:8188`

### 生成画像の場所

```
output/demo_work_001/raw/
├── scene_001/
│   └── （生成画像）
├── scene_002/
│   └── （生成画像）
└── scene_003/
    └── （生成画像）
```

### 次のステップ: 採用・パッケージング

```bash
# 画像採用
python -m src.cli approve demo_work_001 output/demo_work_001/raw/scene_001/ComfyUI_00001_.png

# さらに画像を採用...

# パッケージ化
python -m src.cli package demo_work_001

# 出力先
output/demo_work_001/package/work_demo_work_001.zip
```

## トラブルシューティング

### ComfyUIに接続できない

```bash
# 接続確認
curl http://localhost:8188/system_stats

# ComfyUIが起動しているか確認
ps aux | grep comfy
```

### モデルが見つからない

ComfyUIの`models/checkpoints/`にStable Diffusionモデルを配置してください。
`workflows/default.json`の`ckpt_name`を実際のモデル名に変更:

```json
{
  "4": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "your_model_name.safetensors"
    }
  }
}
```

### Dry-runモードで試す

ComfyUIなしでワークフローをテスト:

```bash
# config/settings.yamlで dry_run: true に設定
python examples/demo_workflow.py
```

ログで動作確認ができます（実際の画像は生成されません）。

## より詳しい使い方

詳細は[README.md](README.md)を参照してください。
