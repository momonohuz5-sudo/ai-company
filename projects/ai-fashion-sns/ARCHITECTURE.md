# 技術設計（MVP）

`PLAN.md` で確定した内容を、実際に動かすための技術設計としてまとめる。

## パイプライン全体

```
[毎朝の起動]
   │
   ├─ 1. 本日のアートスタイル・テーマを決定 (Claude、創作的に決定。トレンド調査は不要)
   ├─ 2. プロンプト生成       (Claude)
   ├─ 3. 画像生成 20枚        (Gemini API + Grok API)
   ├─ 4. 採点                (Claude, vision入力)
   ├─ 5. 上位5枚を選定        (Claude)
   ├─ 6. 画像補正             (Stability AI Fast Upscale, 任意・未設定ならスキップ)
   └─ 7. リポジトリのoutput/に保存してgit push (★自動化範囲はここまで)
        │
        (X投稿はCEOが手動)
        │
   ├─ 8. いいね数取得         (手動 or X API読み取り、要決定)
   └─ 9. 学習・翌日への反映   (Claude が前日ログを見て改善案を出す。性的訴求の強化は行わない)
```

コンセプトは「女性を被写体にしたポートレート・アート作品集」（PLAN.md参照）。ファッション/トレンド紹介ではないため、トレンド取得ステップは廃止した。

※ Googleドライブへの保存はOAuth設定が手間なため、当面リポジトリ内保存に変更した（下記「保存先について」参照）。

## 実行環境: 案A（推奨） vs 案B

| | 案A: Claude Code Routine | 案B: 自前PC + cron/タスクスケジューラ |
|---|---|---|
| 起動条件 | PCを起動しておく必要なし | 毎朝PCが起動している必要あり |
| APIキー管理 | この環境の環境変数として保存 | 手元のPCで完全管理 |
| 実装の手間 | Routine（`create_trigger`）を1つ設定するだけ | スケジューラ設定＋常駐スクリプトの保守が必要 |

**推奨は案A。** 毎朝 `create_trigger`（cron指定、`create_new_session_on_fire: true`）でこの環境に新規セッションを起こし、下記スクリプト群を実行させる。

## モジュール構成（`projects/ai-fashion-sns/pipeline/`）

```
pipeline/
├── README.md            セットアップ手順・必要なAPIキー一覧
├── requirements.txt      Python依存パッケージ
├── .env.example           必要な環境変数のテンプレート（実キーはコミットしない）
├── config.py              設定読み込み（生成枚数、保存先パスなど）
├── image_gen.py           Gemini/Grok APIを呼び出して画像を生成する
├── retouch.py             Stability AI Fast Upscale（Meitu代替）を呼び出す
├── repo_save.py           補正済み画像をリポジトリのoutput/に保存する
├── output/                保存された画像（日付ごとのフォルダ）
├── state_store.py         毎日の実行ログ（プロンプト・スコア・選定結果・後日の反応）を保存
└── main.py                上記を順に呼び出すエントリーポイント
```

- アートスタイル決定・プロンプト生成・採点・学習分析は、Claude（このエージェント自身）が `main.py` を呼び出しながら直接行うため、専用モジュールを持たない。
- `image_gen.py` / `retouch.py` は外部APIを叩く部分のみを担当する薄いラッパーとする。

## 保存先について

当初はGoogleドライブへの保存を予定していたが、組織ポリシーでサービスアカウント鍵の発行がブロックされ、OAuth(デスクトップアプリ)方式も設定の手間が大きいと判断し、**当面はリポジトリ内保存（`pipeline/output/YYYY-MM-DD/`）に変更**した。

- `repo_save.py` が画像をファイルとして保存する
- 保存後、Routineがそのままgit commit & pushする（既存の仕組みをそのまま利用）
- 将来Googleドライブ等の外部ストレージに切り替えたくなった場合は、`repo_save.py` と同じインターフェース（`save(image_bytes, filename) -> str`）を持つモジュールに差し替えるだけでよい設計にしている

## 状態・学習ループの設計

- `state_store.py` が日次ログ（JSON）を `pipeline/logs/YYYY-MM-DD.json` に保存する。
- ログの中身: その日使ったプロンプト、生成した20枚の情報、Claudeの採点、選ばれた5枚、（後日）いいね数等の反応。
- 翌朝の実行時に前日ログを読み込み、Claudeが「どのプロンプト傾向が良かったか」を分析してプロンプト生成に反映する。

## シークレット管理

- Gemini / Grok / Stability AI のAPIキーは、この環境の環境変数として登録し、リポジトリにはコミットしない。
- `.env.example` にキー名だけを記載し、実際の値は含めない。
- GEMINI_API_KEY / GROK_API_KEY は登録済み（必須）。STABILITY_API_KEY は任意（未設定なら`retouch.py`が補正をスキップし元画像をそのまま使う）。

## 実行スケジュール（設定済み）

案Aを採用し、Claude Code Remote の Routine を設定済み。

- Routine名: 「AIポートレート・アート作品集パイプライン（毎朝9時JST）」
- trigger_id: `trig_01PHaSPkAPz7LDRKYYBbnVVh`
- 実行時刻: 毎朝9:00（JST）= cron `0 0 * * *`（UTC）
- 挙動: 起動のたびに新規セッションで、まずGEMINI_API_KEY/GROK_API_KEYの設定状況を確認。未設定なら実行せず「未設定のためスキップ」と通知するだけに留める。設定済みならパイプライン本体（アートテーマ決定〜output/保存〜git push〜ログ保存）を実行する。STABILITY_API_KEYは任意のため起動条件には含めない。

## 未確定事項（次に決めること）

- STABILITY_API_KEYの取得（任意、画像補正の質を上げたくなったら対応）
- いいね数の取得方法（X API読み取り連携 or 手動入力）
