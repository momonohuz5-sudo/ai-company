"""ポーカーレンジチャート描画エンジン

GTOwizardスタイルの13×13レンジチャートを生成します。
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple


class RangeChartRenderer:
    """13×13レンジチャート描画クラス"""

    # 13×13マトリックスの定義（AA=左上、22=右下）
    RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

    # アクション色定義（GTOwizardスタイル）
    COLORS = {
        "fold": "#4A90E2",       # 青
        "call": "#7ED321",       # 緑
        "raise": "#F5A623",      # オレンジ
        "allin": "#D0021B",      # 濃赤
        "check": "#CCCCCC",      # グレー
    }

    def __init__(self):
        """初期化"""
        self.fig = None
        self.ax = None

    def create_range_matrix(self) -> List[List[str]]:
        """13×13のハンド文字列マトリックスを作成

        Returns:
            List[List[str]]: ハンド文字列の2次元配列
        """
        matrix = []
        for i, rank1 in enumerate(self.RANKS):
            row = []
            for j, rank2 in enumerate(self.RANKS):
                if i == j:
                    # ペア（対角線）
                    hand = f"{rank1}{rank2}"
                elif i < j:
                    # スーテッド（対角線より上）
                    hand = f"{rank1}{rank2}s"
                else:
                    # オフスーテッド（対角線より下）
                    hand = f"{rank2}{rank1}o"
                row.append(hand)
            matrix.append(row)
        return matrix

    def render_chart(
        self,
        range_data: Dict[str, str],
        title: str = "Range Chart",
        output_path: Path = None,
    ) -> Path:
        """レンジチャートを描画

        Args:
            range_data: ハンド→アクションの辞書 {"AA": "allin", "AKs": "raise", ...}
            title: チャートタイトル
            output_path: 保存先パス

        Returns:
            Path: 保存されたファイルのパス
        """
        # マトリックス作成
        hand_matrix = self.create_range_matrix()

        # 色マッピング用の数値マトリックス作成
        action_to_num = {
            "fold": 0,
            "call": 1,
            "raise": 2,
            "allin": 3,
            "check": 4,
        }

        color_matrix = np.zeros((13, 13))
        for i, row in enumerate(hand_matrix):
            for j, hand in enumerate(row):
                action = range_data.get(hand, "fold")
                color_matrix[i, j] = action_to_num.get(action, 0)

        # 図の作成
        fig, ax = plt.subplots(figsize=(10, 10))

        # カラーマップ
        colors_list = [self.COLORS[action] for action in ["fold", "call", "raise", "allin", "check"]]
        cmap = ListedColormap(colors_list)

        # ヒートマップ描画
        im = ax.imshow(color_matrix, cmap=cmap, vmin=0, vmax=4)

        # グリッド線
        ax.set_xticks(np.arange(13))
        ax.set_yticks(np.arange(13))
        ax.set_xticklabels(self.RANKS)
        ax.set_yticklabels(self.RANKS)

        # マス目の境界線
        ax.set_xticks(np.arange(13) - 0.5, minor=True)
        ax.set_yticks(np.arange(13) - 0.5, minor=True)
        ax.grid(which="minor", color="white", linestyle='-', linewidth=2)

        # テキスト表示（ハンド名）
        for i in range(13):
            for j in range(13):
                hand = hand_matrix[i][j]
                text_color = "white" if color_matrix[i, j] >= 2 else "black"
                ax.text(j, i, hand, ha="center", va="center",
                       color=text_color, fontsize=10, weight="bold")

        # タイトル
        ax.set_title(title, fontsize=16, weight="bold", pad=20)

        # 凡例
        legend_elements = [
            mpatches.Patch(facecolor=self.COLORS["fold"], label="Fold"),
            mpatches.Patch(facecolor=self.COLORS["call"], label="Call"),
            mpatches.Patch(facecolor=self.COLORS["raise"], label="Raise"),
            mpatches.Patch(facecolor=self.COLORS["allin"], label="All-in"),
        ]
        ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1.05, 1))

        plt.tight_layout()

        # 保存
        if output_path is None:
            output_path = Path("range_chart.png")

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return output_path

    def render_comparison_chart(
        self,
        range_data_list: List[Tuple[Dict[str, str], str]],
        title: str = "Range Comparison",
        output_path: Path = None,
    ) -> Path:
        """複数のレンジチャートを並べて比較表示

        Args:
            range_data_list: [(range_data, subtitle), ...] のリスト
            title: 全体タイトル
            output_path: 保存先パス

        Returns:
            Path: 保存されたファイルのパス
        """
        n_charts = len(range_data_list)
        fig, axes = plt.subplots(1, n_charts, figsize=(10 * n_charts, 10))

        if n_charts == 1:
            axes = [axes]

        for ax, (range_data, subtitle) in zip(axes, range_data_list):
            # 各チャートを描画（簡略版）
            hand_matrix = self.create_range_matrix()
            action_to_num = {"fold": 0, "call": 1, "raise": 2, "allin": 3, "check": 4}

            color_matrix = np.zeros((13, 13))
            for i, row in enumerate(hand_matrix):
                for j, hand in enumerate(row):
                    action = range_data.get(hand, "fold")
                    color_matrix[i, j] = action_to_num.get(action, 0)

            colors_list = [self.COLORS[action] for action in ["fold", "call", "raise", "allin", "check"]]
            cmap = ListedColormap(colors_list)

            im = ax.imshow(color_matrix, cmap=cmap, vmin=0, vmax=4)
            ax.set_xticks(np.arange(13))
            ax.set_yticks(np.arange(13))
            ax.set_xticklabels(self.RANKS)
            ax.set_yticklabels(self.RANKS)
            ax.set_xticks(np.arange(13) - 0.5, minor=True)
            ax.set_yticks(np.arange(13) - 0.5, minor=True)
            ax.grid(which="minor", color="white", linestyle='-', linewidth=2)

            for i in range(13):
                for j in range(13):
                    hand = hand_matrix[i][j]
                    text_color = "white" if color_matrix[i, j] >= 2 else "black"
                    ax.text(j, i, hand, ha="center", va="center",
                           color=text_color, fontsize=8, weight="bold")

            ax.set_title(subtitle, fontsize=14, weight="bold")

        fig.suptitle(title, fontsize=18, weight="bold")
        plt.tight_layout()

        if output_path is None:
            output_path = Path("range_comparison.png")

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return output_path


# サンプルレンジデータ
SAMPLE_RANGES = {
    "tight_preflop": {
        "AA": "allin", "KK": "allin", "QQ": "allin", "JJ": "raise",
        "AKs": "raise", "AKo": "raise", "AQs": "raise", "AQo": "call",
        "TT": "raise", "99": "call", "88": "call",
    },
    "loose_preflop": {
        "AA": "allin", "KK": "allin", "QQ": "raise", "JJ": "raise", "TT": "raise",
        "AKs": "raise", "AKo": "raise", "AQs": "raise", "AQo": "raise",
        "AJs": "raise", "AJo": "call", "ATs": "raise", "ATo": "call",
        "99": "raise", "88": "call", "77": "call", "66": "call",
        "KQs": "raise", "KJs": "call", "QJs": "call",
    },
}
