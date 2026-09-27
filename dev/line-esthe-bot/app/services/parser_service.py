import re
from dataclasses import dataclass
from enum import Enum

from app.models.parsed_query import ParsedQuery

# "の" is treated as a separator only between two non-space tokens (e.g. "ABC新宿のあい"),
# never inside a single token, to avoid splitting shop/therapist names that legitimately
# contain "の".
_NO_SEPARATOR = re.compile(r"^(\S+?)の(\S+)$")


class ParseStatus(Enum):
    OK = "ok"
    MISSING_SHOP = "missing_shop"
    UNPARSEABLE = "unparseable"


@dataclass
class ParseResult:
    status: ParseStatus
    query: ParsedQuery | None = None


def parse_query(raw_text: str) -> ParseResult:
    text = raw_text.strip()
    if not text:
        return ParseResult(status=ParseStatus.UNPARSEABLE)

    # Split on whitespace (spaces, tabs, newlines) first.
    tokens = [t for t in re.split(r"\s+", text) if t]

    if len(tokens) >= 2:
        shop, therapist = tokens[0], tokens[1]
        return ParseResult(
            status=ParseStatus.OK,
            query=ParsedQuery(shop_name=shop, therapist_name=therapist),
        )

    # Single whitespace-delimited token: try "店舗名の名前" form.
    match = _NO_SEPARATOR.match(tokens[0])
    if match:
        shop, therapist = match.group(1), match.group(2)
        return ParseResult(
            status=ParseStatus.OK,
            query=ParsedQuery(shop_name=shop, therapist_name=therapist),
        )

    # Only one identifiable name with no shop context.
    return ParseResult(status=ParseStatus.MISSING_SHOP)
