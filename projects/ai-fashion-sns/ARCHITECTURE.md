# 技術設計（MVP）

`PLAN.md` で確定した内容を、実際に動かすための技術設計としてまとめる。

## パイプライン全体

```
[毎朝の起動]
   │
   ├─ 1. トレンド取得        (Claude / WebSearch)
   ├─ 2. 流行りの服装取得     (Claude / WebSearch)
   ├─ 3. プロンプト生成       (Claude)
   ├─ 4. 画像生成 20枚        (Gemini API + Grok API)
   ├─ 5. 採点                (Claude, vision入力)
   ├─ 6. 上位5枚を選定        (Claude)
   ├─ 7. 画像補正             (Stability AI / Photoroom 等API)
   └─ 8. Googleドライブへ保存 (Google Drive API)   ★自動化範囲はここまで
        │
        (X投稿はCEOが手動)
        │
   ├─ 9. いいね数取得         (手動 or X API読み取り、要決定)
   └─10. 学習・翌日への反映   (Claude が前日ログを見て改善案を出す)
```

## 実行環境: 案A（推奨） vs 案B

| | 案A: Claude Code Routine | 案B: 自前PC + cron/タスクスケジューラ |
|---|---|---|
| トレンド取得 | Claude内蔵のWebSearchで追加コストなし | 自前の検索API/スクレイピングが必要 |
| 起動条件 | PCを起動しておく必要なし | 毎朝PCが起動している必要あり |
| APIキー管理 | この環境のシークレットとして保存 | 手元のPCで完全管理 |
| 実装の手間 | Routine（`create_trigger`）を1つ設定するだけ | スケジューラ設定＋常駐スクリプトの保守が必要 |

**推奨は案A。** 毎朝 `create_trigger`（cron指定、`create_new_session_on_fire: true`）でこの環境に新規セッションを起こし、下記スクリプト群を実行させる。

## モジュール構成（`projects/ai-fashion-sns/pipeline/`）

```
pipeline/
├── README.md            セットアップ手順・必要なAPIキー一覧
├── requirements.txt      Python依存パッケージ
├── .env.example           必要な環境変数のテンプレート（実キーはコミットしない）
├── config.py              設定読み込み（生成枚数、保存先フォルダIDなど）
├── image_gen.py           Gemini/Grok APIを呼び出して画像を生成する
├── retouch.py             画像補正API（Meitu代替）を呼び出す
├── drive_upload.py        Google Drive APIへのアップロード
├── state_store.py         毎日の実行ログ（プロンプト・スコア・選定結果・後日の反応）を保存
└── main.py                上記を順に呼び出すエントリーポイント
```

- トレンド取得・プロンプト生成・採点・学習分析は、Claude（このエージェント自身）が `main.py` を呼び出しながら直接行うため、専用モジュールを持たない（Claude Code のWebSearch/推論をそのまま使う）。
- `image_gen.py` / `retouch.py` / `drive_upload.py` は外部APIを叩く部分のみを担当する薄いラッパーとする。

## 状態・学習ループの設計

- `state_store.py` が日次ログ（JSON）を `pipeline/logs/YYYY-MM-DD.json` に保存する。
- ログの中身: その日使ったプロンプト、生成した20枚の情報、Claudeの採点、選ばれた5枚、（後日）いいね数等の反応。
- 翌朝の実行時に前日ログを読み込み、Claudeが「どのプロンプト傾向が良かったか」を分析してプロンプト生成に反映する。

## シークレット管理

- Gemini / Grok / 画像補正API / Google Drive のAPIキー・認証情報は `.env`（gitignore対象）またはこの環境のシークレットストアに保存し、リポジトリにはコミットしない。
- `.env.example` にキー名だけを記載し、実際の値は含めない。

## 未確定事項（次に決めること）

- いいね数の取得方法（X API読み取り連携 or 手動入力）
- 画像補正APIの最終選定（Stability AI / Photoroom 等の実際の比較検証）
- 実行時刻（毎朝何時に起動するか）
