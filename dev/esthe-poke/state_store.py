"""PokeUnitState をプロセス間(cron起動のたび)で永続化するための簡易JSONストア。"""

from __future__ import annotations

import json
import os
from datetime import datetime

from config import POKE_UNITS, STATE_FILE_PATH_ENV
from rules import PokeUnitState

_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), ".state.json")


def _state_file_path() -> str:
    return os.environ.get(STATE_FILE_PATH_ENV, _DEFAULT_PATH)


def load_states() -> dict[str, PokeUnitState]:
    path = _state_file_path()
    states = {unit.id: PokeUnitState(unit_id=unit.id) for unit in POKE_UNITS}

    if not os.path.exists(path):
        return states

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    for unit_id, data in raw.items():
        if unit_id not in states:
            continue
        states[unit_id] = PokeUnitState(
            unit_id=unit_id,
            pokes_today=data["pokes_today"],
            last_poke_at=datetime.fromisoformat(data["last_poke_at"]) if data["last_poke_at"] else None,
            last_reset_day=datetime.fromisoformat(data["last_reset_day"]) if data["last_reset_day"] else None,
        )
    return states


def save_states(states: dict[str, PokeUnitState]) -> None:
    raw = {
        unit_id: {
            "pokes_today": state.pokes_today,
            "last_poke_at": state.last_poke_at.isoformat() if state.last_poke_at else None,
            "last_reset_day": state.last_reset_day.isoformat() if state.last_reset_day else None,
        }
        for unit_id, state in states.items()
    }
    path = _state_file_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
