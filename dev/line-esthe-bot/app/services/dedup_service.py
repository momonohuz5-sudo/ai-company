import re

from app.models.review import Review

# Strips whitespace/newlines and common punctuation/symbol noise so reviews
# reposted verbatim across sites (or with trivial formatting differences)
# are recognized as duplicates. Spec section 22: exact-match dedup for now,
# with embedding-based similarity left as a future extension.
_SYMBOL_PATTERN = re.compile(r"[\s!-/:-@\[-`{-~、。！？「」『』・…　]+")


def _normalize(text: str) -> str:
    return _SYMBOL_PATTERN.sub("", text)


def dedup_reviews(reviews: list[Review]) -> list[Review]:
    seen: set[str] = set()
    deduped: list[Review] = []
    for review in reviews:
        key = _normalize(review.text)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(review)
    return deduped
