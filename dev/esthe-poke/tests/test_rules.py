from datetime import datetime, timedelta, timezone

from rules import (
    AvailabilitySnapshot,
    Event,
    PokeUnitState,
    business_day_start,
    decide,
    is_within_poke_window,
    snap_forbidden_minute,
)

JST = timezone(timedelta(hours=9))


def dt(hour: int, minute: int, day: int = 1) -> datetime:
    return datetime(2026, 7, day, hour, minute, tzinfo=JST)


def test_snap_forbidden_minute_late_in_hour():
    assert snap_forbidden_minute(dt(14, 57)) == dt(14, 53)


def test_snap_forbidden_minute_early_in_next_hour():
    assert snap_forbidden_minute(dt(15, 5)) == dt(14, 53)


def test_snap_forbidden_minute_exact_half_hour():
    assert snap_forbidden_minute(dt(14, 30)) == dt(14, 23)


def test_snap_forbidden_minute_untouched():
    assert snap_forbidden_minute(dt(14, 20)) == dt(14, 20)


def test_poke_window_covers_10am_to_2730():
    assert is_within_poke_window(dt(10, 0)) is True
    assert is_within_poke_window(dt(3, 30, day=2)) is True  # 翌27:30
    assert is_within_poke_window(dt(4, 0, day=2)) is False  # 翌28:00相当
    assert is_within_poke_window(dt(9, 59)) is False


def test_decide_blocks_outside_poke_window():
    state = PokeUnitState(unit_id="u")
    availability = AvailabilitySnapshot(now=dt(5, 0, day=2), events=())
    decision = decide(state, dt(5, 0, day=2), availability, other_areas_busy=False)
    assert decision.should_poke is False


def test_decide_blocks_when_quota_exhausted():
    now = dt(12, 0)
    state = PokeUnitState(unit_id="u", pokes_today=10, last_reset_day=business_day_start(now))
    availability = AvailabilitySnapshot(now=now, events=())
    decision = decide(state, now, availability, other_areas_busy=False)
    assert decision.should_poke is False
    assert "上限" in decision.reason


def test_decide_blocks_within_base_interval():
    now = dt(12, 0)
    state = PokeUnitState(unit_id="u", last_poke_at=now - timedelta(minutes=30))
    availability = AvailabilitySnapshot(now=now, events=())
    decision = decide(state, now, availability, other_areas_busy=False)
    assert decision.should_poke is False
    assert "1時間40分" in decision.reason


def test_decide_blocks_when_occupied_with_no_future_opening():
    now = dt(12, 0)
    state = PokeUnitState(unit_id="u")
    events = (Event(start=dt(10, 0), end=dt(4, 0, day=2)),)  # ポチ可能時間(翌27:30まで)を超えて埋まっている
    availability = AvailabilitySnapshot(now=now, events=events)
    decision = decide(state, now, availability, other_areas_busy=False)
    assert decision.should_poke is False
    assert "空き" in decision.reason


def test_decide_pokes_15min_before_next_opening():
    events = (Event(start=dt(11, 0), end=dt(13, 0)),)
    state = PokeUnitState(unit_id="u")

    too_early = AvailabilitySnapshot(now=dt(12, 30), events=events)
    assert decide(state, dt(12, 30), too_early, other_areas_busy=False).should_poke is False

    at_ideal = AvailabilitySnapshot(now=dt(12, 45), events=events)
    decision = decide(state, dt(12, 45), at_ideal, other_areas_busy=False)
    assert decision.should_poke is True
    assert "15分前" in decision.reason


def test_decide_pokes_when_free_now_and_interval_ok():
    state = PokeUnitState(unit_id="u", last_poke_at=dt(10, 0))
    availability = AvailabilitySnapshot(now=dt(12, 0), events=())
    decision = decide(state, dt(12, 0), availability, other_areas_busy=False)
    assert decision.should_poke is True


def test_decide_recommends_poke_when_other_areas_busy():
    state = PokeUnitState(unit_id="u")
    availability = AvailabilitySnapshot(now=dt(12, 0), events=())
    decision = decide(state, dt(12, 0), availability, other_areas_busy=True)
    assert decision.should_poke is True
    assert "他エリア" in decision.reason


def test_record_poke_increments_and_resets_daily():
    state = PokeUnitState(unit_id="u")
    state.record_poke(dt(11, 0))
    assert state.pokes_today == 1
    state.reset_if_new_day(dt(11, 0, day=2))
    assert state.pokes_today == 0
