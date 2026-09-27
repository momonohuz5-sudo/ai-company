from dataclasses import dataclass, field


@dataclass
class SummaryResult:
    review_count: int
    summary_points: list[str] = field(default_factory=list)
    mixed_opinion: bool = False
