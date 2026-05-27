"""ポーカー戦略note記事生成 - メインエントリーポイント"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.content_generator import ContentGenerator
from src.range_chart_renderer import RangeChartRenderer, SAMPLE_RANGES


def test_content_generation():
    """記事生成のテスト"""
    print("=== ポーカー戦略記事生成テスト ===\n")

    # 設定バリデーション
    try:
        Config.validate()
        print("✓ 設定OK\n")
    except ValueError as e:
        print(f"✗ 設定エラー: {e}")
        print("\n.envファイルを作成し、ANTHROPIC_API_KEYを設定してください。")
        print("例: cp .env.example .env")
        return

    # 記事生成テスト
    try:
        generator = ContentGenerator()
        print("✓ ContentGenerator初期化OK\n")

        print("記事生成中...")
        article = generator.generate_article(
            topic="プリフロップレンジの基本",
            difficulty=1,  # 初級
            specific_scenario="BTN（ボタン）からのオープンレイズ戦略",
            include_chart=True
        )

        print(f"✓ 記事生成完了\n")
        print(f"タイトル: {article['title']}")
        print(f"難易度: {'★' * article['difficulty']}")
        print(f"文字数: {len(article['content'])}字")
        print(f"トークン使用量:")
        print(f"  - Input: {article['metadata']['tokens']['input']}")
        print(f"  - Output: {article['metadata']['tokens']['output']}")
        print(f"  - Cache Read: {article['metadata']['tokens']['cache_read']}")
        print(f"  - Cache Creation: {article['metadata']['tokens']['cache_creation']}")

        # 保存
        filepath = generator.save_article(article)
        print(f"\n✓ 保存完了: {filepath}\n")

        # チャートデータがあれば描画
        if article.get("chart_data"):
            print("レンジチャート生成中...")
            renderer = RangeChartRenderer()
            chart_path = Config.IMAGES_DIR / "test_range_chart.png"
            renderer.render_chart(
                range_data=article["chart_data"]["range_data"],
                title=article["chart_data"]["chart_title"],
                output_path=chart_path
            )
            print(f"✓ チャート生成完了: {chart_path}\n")

    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()


def test_range_chart():
    """レンジチャート描画のテスト"""
    print("=== レンジチャート描画テスト ===\n")

    try:
        renderer = RangeChartRenderer()

        # 単一チャート
        print("単一チャート生成中...")
        chart_path = Config.IMAGES_DIR / "sample_tight_range.png"
        renderer.render_chart(
            range_data=SAMPLE_RANGES["tight_preflop"],
            title="Tight Preflop Range (UTG)",
            output_path=chart_path
        )
        print(f"✓ 生成完了: {chart_path}\n")

        # 比較チャート
        print("比較チャート生成中...")
        comparison_path = Config.IMAGES_DIR / "sample_comparison.png"
        renderer.render_comparison_chart(
            range_data_list=[
                (SAMPLE_RANGES["tight_preflop"], "Tight (UTG)"),
                (SAMPLE_RANGES["loose_preflop"], "Loose (BTN)"),
            ],
            title="Preflop Range Comparison",
            output_path=comparison_path
        )
        print(f"✓ 生成完了: {comparison_path}\n")

    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()


def test_workflow():
    """ワークフロー統合テスト（モック投稿）"""
    print("=== ワークフロー統合テスト ===\n")

    try:
        from src.workflow import ArticleWorkflow

        # モックモードで実行（実際には投稿しない）
        workflow = ArticleWorkflow(use_mock=True)

        print("記事生成・投稿ワークフロー実行中...\n")
        result = workflow.generate_and_publish(
            topic="プリフロップレンジの基本",
            difficulty=1,
            specific_scenario="BTNからのオープンレイズ戦略",
            hashtags=["ポーカー", "ポーカー戦略", "初心者"],
            publish_immediately=True,
        )

        if result["success"]:
            print("\n✓ ワークフロー完了\n")
            print(f"タイトル: {result['article']['title']}")
            print(f"note URL: {result['note_url']}")
            print(f"生成チャート: {len(result['chart_paths'])}枚")
        else:
            print(f"\n✗ ワークフローエラー: {result['error']}")

    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()


def test_batch_generation():
    """バッチ生成テスト（週間記事5本）"""
    print("=== バッチ生成テスト（週間記事5本） ===\n")

    try:
        from src.workflow import ArticleWorkflow, WEEKLY_TOPICS

        # 最初の3本のみテスト
        test_topics = WEEKLY_TOPICS[:3]

        workflow = ArticleWorkflow(use_mock=True)
        print(f"{len(test_topics)}本の記事を生成中...\n")

        results = workflow.batch_generate(
            topics=test_topics,
            publish=True,
        )

        # サマリー
        print("\n" + "="*60)
        print("バッチ生成結果:")
        for i, result in enumerate(results, 1):
            status = "✓" if result["success"] else "✗"
            title = result["article"]["title"] if result.get("article") else "N/A"
            print(f"{status} {i}. {title}")
        print("="*60 + "\n")

    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description="ポーカー戦略note記事生成システム")
    parser.add_argument(
        "mode",
        choices=["test-content", "test-chart", "test-workflow", "test-batch", "all"],
        help="実行モード"
    )

    args = parser.parse_args()

    if args.mode == "test-content":
        test_content_generation()
    elif args.mode == "test-chart":
        test_range_chart()
    elif args.mode == "test-workflow":
        test_workflow()
    elif args.mode == "test-batch":
        test_batch_generation()
    elif args.mode == "all":
        test_range_chart()
        print("\n" + "="*50 + "\n")
        test_content_generation()
        print("\n" + "="*50 + "\n")
        test_workflow()


if __name__ == "__main__":
    main()
