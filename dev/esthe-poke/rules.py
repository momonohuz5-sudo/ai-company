"""ポチ（リアルタイム集客）判定ルールエンジン。

「ポチ早見表」で共有されたルールを実装したもの。前提が曖昧だった箇所は
コメントで明示しているので、実際の挙動と食い違う場合はここを調整する。

ルール概要:
- ポチはエリア(PokeUnit)ごとに1日10回まで
- 基本間隔は1時間40分に1回
- 理想タイミングは「ご案内可能時刻の15分前」
- 毎時55分〜次の10分は禁止帯(53分にスナップ)、ちょうど30分も禁止(23分にスナップ)
- 施術中・直近で案内不可なら禁止
- 他エリアが混雑していて、かつ自エリアが即案内可能なら推奨ポチ
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

BUSINESS_START_HOUR = 10  # 10:00 開店
POKE_WINDOW_HOURS = 27.5 - 10  # 10:00〜27:30(翌3:30)がポチ可能時間

MAX_POKES_PER_DAY = 10
BASE_INTERVAL = timedelta(minutes=100)  # 1時間40分
LEAD_TIME = timedelta(minutes=15)


def business_day_start(now: datetime) -> datetime:
    """営業日の起点(当日10:00)を返す。10:00より前なら前日10:00扱い。"""
    anchor = now.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
    if now < anchor:
        anchor -= timedelta(days=1)
    return anchor


def poke_window_end(now: datetime) -> datetime:
    return business_day_start(now) + timedelta(hours=POKE_WINDOW_HOURS)


def is_within_poke_window(now: datetime) -> bool:
    start = business_day_start(now)
    return start <= now <= poke_window_end(now)


def snap_forbidden_minute(dt: datetime) -> datetime:
    """禁止帯を避けて安全な分にスナップする。

    - 毎時55分〜59分 -> その時の53分
    - 翌時0分〜10分  -> 直前の時の53分
    - ちょうど30分   -> その時の23分
    """
    minute = dt.minute
    if minute == 30:
        return dt.replace(minute=23, second=0, microsecond=0)
    if minute >= 55:
        return dt.replace(minute=53, second=0, microsecond=0)
    if minute <= 10:
        return (dt - timedelta(hours=1)).replace(minute=53, second=0, microsecond=0)
    return dt


@dataclass
class Event:
    start: datetime
    end: datetime


@dataclass
class AvailabilitySnapshot:
    """あるポチユニットの、ある時点における空き状況。

    events はカレンダー予定(施術・接客中の時間帯)の一覧。
    複数セラピスト/複数カレンダーがある場合は事前にマージして渡す。
    """

    now: datetime
    events: tuple[Event, ...]

    def is_free_now(self) -> bool:
        return not any(e.start <= self.now < e.end for e in self.events)

    def next_free_slot_start(self, horizon: datetime) -> datetime | None:
        """次に空くタイミング(horizon まで)。今空いていれば now を返す。"""
        if self.is_free_now():
            return self.now
        candidates = sorted(e.end for e in self.events if e.end > self.now)
        for candidate in candidates:
            if candidate > horizon:
                return None
            if not any(e.start <= candidate < e.end for e in self.events):
                return candidate
        return None


@dataclass
class PokeUnitState:
    unit_id: str
    pokes_today: int = 0
    last_poke_at: datetime | None = None
    last_reset_day: datetime | None = None

    def reset_if_new_day(self, now: datetime) -> None:
        today_start = business_day_start(now)
        if self.last_reset_day != today_start:
            self.pokes_today = 0
            self.last_reset_day = today_start

    def record_poke(self, when: datetime) -> None:
        self.pokes_today += 1
        self.last_poke_at = when


@dataclass
class PokeDecision:
    should_poke: bool
    reason: str


def decide(
    state: PokeUnitState,
    now: datetime,
    availability: AvailabilitySnapshot,
    other_areas_busy: bool,
) -> PokeDecision:
    state.reset_if_new_day(now)

    if not is_within_poke_window(now):
        return PokeDecision(False, "ポチ可能時間(10:00〜27:30)外")

    if state.pokes_today >= MAX_POKES_PER_DAY:
        return PokeDecision(False, "本日の上限(10回/日)に到達")

    if state.last_poke_at is not None and now - state.last_poke_at < BASE_INTERVAL:
        return PokeDecision(False, "前回ポチから1時間40分経過していない")

    horizon = poke_window_end(now)
    free_now = availability.is_free_now()
    next_free = availability.next_free_slot_start(horizon)

    if not free_now and next_free is None:
        return PokeDecision(False, "直近で案内可能な空きがない")

    if not free_now:
        ideal = snap_forbidden_minute(next_free - LEAD_TIME)
        if now < ideal:
            return PokeDecision(False, "ご案内可能時刻の15分前にまだ達していない")
        return PokeDecision(True, "ご案内可能時刻の15分前")

    if other_areas_busy:
        return PokeDecision(True, "他エリア混雑・自エリア即案内可能のため推奨ポチ")

    return PokeDecision(True, "即案内可能・基本間隔クリア")
