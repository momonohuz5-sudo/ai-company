from app.models.summary import SummaryResult


def _closing_line(review_count: int, mixed_opinion: bool) -> str:
    if mixed_opinion:
        return "という感じで、評価が分かれているみたい！"
    if review_count <= 1:
        return "こんな口コミがみられたよ！"
    if review_count <= 3:
        return "という声が複数の口コミでみられたよ！"
    return "という口コミが多くみられたよ！"


def build_summary_message(therapist_name: str, summary: SummaryResult) -> str:
    header = f"{therapist_name}さんのレビューはこんな感じ！"
    bullets = "\n".join(f"・{point}" for point in summary.summary_points)
    closing = _closing_line(summary.review_count, summary.mixed_opinion)
    return f"{header}\n{bullets}\n{closing}"
