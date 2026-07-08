"""ポチ自動化のエントリポイント。2〜3分おきにcronから起動される想定。

1回の起動で全ポチユニットをチェックし、条件を満たしたものだけポチする。
状態(本日の消化回数・前回ポチ時刻)は state_store 経由でファイルに永続化する。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import calendar_client
import notifier
import site_actions
import state_store
from config import POKE_UNITS
from rules import AvailabilitySnapshot, decide, poke_window_end

JST = ZoneInfo("Asia/Tokyo")


def _build_availability(unit, now: datetime) -> AvailabilitySnapshot:
    import os

    calendar_ids = tuple(os.environ[env_name] for env_name in unit.calendar_ids_env)
    window_end = poke_window_end(now)
    events = calendar_client.fetch_merged_events(calendar_ids, now, window_end)
    return AvailabilitySnapshot(now=now, events=events)


def run_once(now: datetime | None = None) -> None:
    now = now or datetime.now(JST)

    states = state_store.load_states()
    availabilities = {unit.id: _build_availability(unit, now) for unit in POKE_UNITS}

    busy_count = sum(1 for a in availabilities.values() if not a.is_free_now())

    for unit in POKE_UNITS:
        state = states[unit.id]
        availability = availabilities[unit.id]
        # 「他エリアが混雑」= 自分以外のユニットのうち、埋まっているものが半数以上
        other_unit_count = len(POKE_UNITS) - 1
        other_busy_count = busy_count - (0 if availability.is_free_now() else 1)
        other_areas_busy = other_unit_count > 0 and other_busy_count >= other_unit_count / 2

        decision = decide(state, now, availability, other_areas_busy)
        if not decision.should_poke:
            continue

        for site_id in unit.sites:
            site_actions.poke_site(site_id)

        notifier.notify_poke(unit.label, unit.sites, decision.reason)
        state.record_poke(now)

    state_store.save_states(states)


if __name__ == "__main__":
    run_once()
