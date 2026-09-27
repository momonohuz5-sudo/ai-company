from dataclasses import dataclass


@dataclass
class Review:
    source: str
    shop_name: str
    therapist_name: str
    text: str
    url: str | None
    date: str | None
