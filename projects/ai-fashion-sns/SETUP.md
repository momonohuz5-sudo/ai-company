# セットアップ手順書（ローカル/VS Code環境）

「AIポートレート・アート作品集」パイプラインを、ローカルPC（VS Code）でゼロから構築するための手順。
背景・コンセプト・ガードレールは `PLAN.md`、技術設計は `ARCHITECTURE.md` を参照。

## 0. 前提条件

以下がPCにインストール済みであること。

- [Git](https://git-scm.com/)
- [Python 3.10以上](https://www.python.org/)
- [VS Code](https://code.visualstudio.com/)
- [Node.js](https://nodejs.org/)（Claude Code CLIのインストールに必要）
- このGitHubリポジトリ（`momonohuz5-sudo/ai-company`）への読み書き権限があるGitHubアカウント

## 1. Claude Code CLIのインストール

VS Codeのターミナルで実行:

```
npm install -g @anthropic-ai/claude-code
claude login
```

`claude login` でブラウザが開くのでAnthropicアカウントでログインする。

## 2. リポジトリの取得

```
git clone https://github.com/momonohuz5-sudo/ai-company.git
cd ai-company
git fetch origin claude/ai-company-functionality-82s34x
git checkout claude/ai-company-functionality-82s34x
```

VS Codeでこの `ai-company` フォルダを開く（File → Open Folder）。

## 3. 必要なAPIキーの取得

| サービス | 取得先 | 備考 |
|---|---|---|
| Gemini | https://aistudio.google.com/apikey | 発行後、Google Cloud Consoleで紐づくプロジェクトの**課金を有効化**しておくこと（無料枠だけだと画像生成でクォータ0エラーになる） |
| Grok（xAI） | https://console.x.ai | APIキーを発行 |
| Stability AI（任意） | https://platform.stability.ai | 画像補正を使いたい場合のみ。無くてもパイプラインは動く（補正がスキップされるだけ） |

APIキーは絶対にリポジトリにコミットしない。次の手順で `.env` にのみ記入する。

## 4. Python環境のセットアップ

```
cd projects/ai-fashion-sns/pipeline
pip install -r requirements.txt
```

（必要であれば先に `python -m venv venv` → `venv\Scripts\activate`（Windows）/ `source venv/bin/activate`（Mac/Linux）で仮想環境を作ってから実行してもよい）

## 5. `.env` の作成

```
cp .env.example .env
```

`.env` をVS Codeで開き、取得したキーを記入する:

```
GEMINI_API_KEY=（Geminiのキー）
GROK_API_KEY=（Grokのキー）
STABILITY_API_KEY=（任意。Stability AIのキー）
```

`.env` は `.gitignore` 済みなので、これ自体がコミットされることはない。

## 6. パイプラインを1回実行してみる

VS Codeのターミナル（リポジトリのルートディレクトリ）で:

```
claude
```

起動したら、以下をそのまま貼り付けて実行を依頼する:

```
projects/ai-fashion-sns/PLAN.md と ARCHITECTURE.md を読んで、
AIポートレート・アート作品集の毎朝のパイプラインを一度実行してください。
本日のアートテーマを創作的に決定し、pipeline/image_gen.py で
Gemini+Grokにより20枚生成、あなた自身で採点して上位5枚を選び、
pipeline/retouch.py と pipeline/repo_save.py で output/ に保存、
pipeline/state_store.py でログを保存してください。
終わったらgit commit & pushしてください。
```

生成された画像は `projects/ai-fashion-sns/pipeline/output/YYYY-MM-DD/` に保存される。

## 7. 毎朝自動実行したい場合（任意）

ローカルではクラウドのRoutineのような仕組みが無いため、OSのタスクスケジューラで
「毎朝、手順6と同じプロンプトをClaude Codeに渡すコマンド」を実行するように設定する。

- **Windows**: タスクスケジューラでバッチファイル（`claude -p "（上記のプロンプト）"` 相当）を毎朝実行するタスクを登録
- **Mac/Linux**: `crontab -e` で同様のコマンドを毎朝実行するよう登録

（`claude -p "..."` はヘッドレスモードでプロンプトを渡す実行方法。詳細はClaude Code CLIのドキュメントを参照）

PCがその時間に起動していない場合は実行されない点に注意。

## 8. 必ず守るガードレール（再掲、詳細はPLAN.md）

- コンセプトは女性を被写体にしたポートレート・アート作品集。性的な訴求は目的としない、SFW限定。
- 被写体は完全オリジナルの日本人女性（実在人物のコピー・なりすまし禁止）。
- 実在ブランドのロゴ・特徴的な柄はそのまま複製しない。
- 学習ループで性的訴求を強化しない。
- X（旧Twitter）への投稿はCEO本人が手動で行う。自動化範囲は `output/` への保存まで。

## 9. トラブルシューティング

| 症状 | 原因・対処 |
|---|---|
| Gemini画像生成で429エラー（quota exceeded, limit 0） | APIキーのGoogle Cloudプロジェクトで課金が有効化されていない → Cloud Consoleで有効化 |
| Grok呼び出しでネットワークエラー | ローカル実行なら通常発生しない。社内プロキシ等がある場合は要確認 |
| `git push` が失敗する | ローカルのGit認証（`gh auth login` または SSH鍵）が設定されているか確認 |
| `ModuleNotFoundError` | `pip install -r requirements.txt` を実行し忘れていないか確認 |
