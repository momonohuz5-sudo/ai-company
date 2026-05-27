# 仕組みの説明

## 全体フロー

```
1. 作品作成 (Work)
   ↓
2. プロンプトブロック作成
   - quality: 画質設定 + 生成パラメータ
   - character: キャラクター説明
   - setting: 背景・環境
   - lighting: ライティング
   - camera: カメラアングル
   - private: プライベート内容（ツールは参照のみ）
   - negative: ネガティブプロンプト（ツールは参照のみ）
   ↓
3. シーン計画作成
   - 各シーンにブロックIDとseedを割り当て
   - JSONLファイルに保存
   ↓
4. ワークフロー構築
   - ComfyUIワークフローテンプレート読み込み
   - プロンプトブロックを結合
   - パラメータ注入（steps, cfg_scale, etc）
   ↓
5. ComfyUI送信
   - シーンごとにワークフローをPOST
   - /prompt エンドポイント使用
   ↓
6. 画像生成（ComfyUI側）
   ↓
7. 画像整理
   - output/{work_id}/raw/scene_XXX/ に配置
   ↓
8. 採用・不採用判定（人間）
   - approved/ または rejected/ に移動
   ↓
9. パッケージング
   - 連番リネーム（001.png, 002.png, ...）
   - サンプル分離
   - ZIP作成
   - メタデータ出力
   ↓
10. コンプライアンスチェック
    - チェックリスト生成
    - 人間が最終確認
```

## データの流れ

### プロンプトの組み立て

```python
# 例: Scene 1のプロンプト構築

# 一般ブロックを結合
positive = [
    quality.content,      # "masterpiece, best quality, ..."
    character.content,    # "1girl, long hair, ..."
    setting.content,      # "beach, ocean, ..."
    lighting.content,     # "sunset, golden hour, ..."
    camera.content,       # "wide shot, full body, ..."
    private.content       # （外部から読み込み、ツールは読まない）
]

final_positive = ", ".join(positive)

# negative も同様に構築
final_negative = negative.content  # （外部から読み込み）
```

### ComfyUIワークフロー注入

```python
# デフォルトワークフロー（workflows/default.json）
workflow = {
    "6": {  # Positive CLIPTextEncode
        "inputs": {
            "text": "{{positive_prompt}}",  # ← ここに注入
            ...
        }
    },
    "7": {  # Negative CLIPTextEncode
        "inputs": {
            "text": "{{negative_prompt}}",  # ← ここに注入
            ...
        }
    },
    "3": {  # KSampler
        "inputs": {
            "seed": 0,        # ← シーンのseedに置き換え
            "steps": 20,      # ← quality.parameters.stepsに置き換え
            "cfg": 7.0,       # ← quality.parameters.cfg_scaleに置き換え
            ...
        }
    }
}
```

## プライバシー保護の仕組み

### 問題: NSFWなど機密プロンプトをツールが扱うと...

- ❌ ログに露出
- ❌ エラーメッセージに露出
- ❌ Gitに誤コミット
- ❌ デバッグ時に漏洩

### 解決策: OPAQUE参照システム

```
ツール側:
  private_id = "private_001"  # IDだけ保持
  ↓
  ファイル存在チェックのみ
  ✓ data/private/blocks/private_001.json が存在するか？
  ↓
  内容は読まない！
  
ユーザー側:
  手動でJSONファイル作成・編集
  ↓
  data/private/blocks/private_001.json:
  {
    "content": "（実際のNSFW内容など）",
    "tags": []
  }
  
ワークフロー構築時:
  外部スクリプト（demo_workflow.pyなど）が
  JSONファイルを読み込み、ワークフローに注入
  ↓
  ツール本体は内容を一切見ない
```

### ログ出力例（プライバシー保護）

```
✓ GOOD:
  Scene 001 created: quality=quality_hd, character=char_001, 
  private=OPAQUE, negative=OPAQUE, seed=1001

✗ BAD (絶対にこうならない):
  Scene 001 created: quality=quality_hd, character=char_001,
  private="nsfw content here", negative="bad anatomy, ..."
```

## ComfyUI API連携

### エンドポイント

```
POST http://localhost:8188/prompt
Content-Type: application/json

{
  "prompt": {
    "3": { "class_type": "KSampler", ... },
    "4": { "class_type": "CheckpointLoaderSimple", ... },
    ...
  },
  "client_id": "unique-client-id"
}

Response:
{
  "prompt_id": "abc123-def456-...",
  "number": 1,
  "node_errors": {}
}
```

### 生成状況確認

ComfyUIのUIで確認: `http://localhost:8188`

または、WebSocket経由でリアルタイム進捗取得（将来の拡張）

## ファイル構造の意味

```
data/
├── works/              # 作品定義
│   └── my_work.json    # タイトル、説明、ステータス
├── blocks/             # 一般プロンプトブロック
│   ├── quality/
│   ├── character/
│   ├── setting/
│   ├── lighting/
│   └── camera/
├── private/            # 🔒 GITIGNORE対象
│   └── blocks/         # 機密プロンプト（ツールは読まない）
│       ├── private_001.json
│       └── negative_001.json
└── scenes/             # シーン計画
    └── my_work_scenes.jsonl

output/
└── my_work/
    ├── raw/            # ComfyUI出力（シーンごと）
    │   ├── scene_001/
    │   ├── scene_002/
    │   └── scene_003/
    ├── approved/       # 採用画像
    ├── rejected/       # 不採用画像
    └── package/        # 最終パッケージ
        ├── images/     # 連番リネーム済み
        ├── samples/    # サンプル用
        ├── sales/      # 販売用
        ├── metadata.json
        └── work_my_work.zip
```

## カスタマイズポイント

### 1. ワークフローテンプレート

`workflows/`に新しいテンプレートを追加:

```bash
workflows/
├── default.json         # SDXL用
├── sd15.json           # SD1.5用
├── anime.json          # アニメモデル用
└── photorealistic.json # フォトリアル用
```

使用時に指定:
```python
workflow = wm.build_workflow(scene, blocks, private_blocks, template_name="anime")
```

### 2. プロンプトブロックタイプ追加

`src/models.py`と`src/prompt_manager.py`を編集:

```python
valid_types = ["quality", "character", "setting", "lighting", "camera", "pose", "expression"]
```

### 3. 生成パラメータ

`quality`ブロックの`parameters`で調整:

```json
{
  "block_id": "quality_hd",
  "block_type": "quality",
  "content": "masterpiece, best quality",
  "parameters": {
    "steps": 30,          # サンプリングステップ数
    "cfg_scale": 7.5,     # CFG Scale
    "sampler": "euler_a", # サンプラー
    "width": 1024,        # 画像幅
    "height": 1536        # 画像高さ
  }
}
```

## トラブルシューティング

### デバッグモード

ログレベルをDEBUGに:
```python
logger = get_logger("demo", config.logs_dir, level=logging.DEBUG)
```

### ワークフロー確認

生成されたワークフローを保存:
```python
Storage.save_json(Path("debug_workflow.json"), workflow)
```

ComfyUIのUIで読み込んで手動テスト可能

### プライバシーチェック

テスト実行:
```bash
pytest tests/test_privacy.py -v
```

ログファイルで検索:
```bash
grep -i "secret" logs/pipeline.log
# 何も出なければOK
```

## 次のステップ

1. **実際のComfyUI環境で動作確認**
2. **独自のワークフローテンプレート作成**
3. **大量シーン生成のバッチ処理最適化**
4. **WebUIの追加（Streamlit/Flask）**
5. **進捗通知機能（Slack/Discord）**
