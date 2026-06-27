import json
import os
from datetime import datetime, timedelta
import pytz
from src.config import AREAS, TIMEZONE, STATE_FILE, BUSINESS_START_HOUR


class StateManager:
    def __init__(self):
        self.tz = pytz.timezone(TIMEZONE)
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        self.state = self._load()
        self._reset_if_new_day()

    def _load(self) -> dict:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._default_state()

    def _default_state(self) -> dict:
        return {
            k: {
                "clicks_today": 0,
                "last_click_time": None,
                "last_reset_date": None,
                "click_history": [],
            }
            for k in AREAS
        }

    def _business_date(self, now: datetime) -> str:
        # 業務日は10:00リセット。深夜(0〜9時)は前日扱い
        if now.hour < BUSINESS_START_HOUR:
            now = now - timedelta(days=1)
        return now.strftime("%Y-%m-%d")

    def _reset_if_new_day(self):
        now = datetime.now(self.tz)
        today = self._business_date(now)
        changed = False

        for area_key in AREAS:
            if area_key not in self.state:
                self.state[area_key] = self._default_state()[area_key]
                changed = True

            if self.state[area_key].get("last_reset_date") != today:
                self.state[area_key]["clicks_today"] = 0
                self.state[area_key]["last_reset_date"] = today
                changed = True

        if changed:
            self._save()

    def _save(self):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_area_state(self, area_key: str) -> dict:
        self._reset_if_new_day()
        return self.state.get(area_key, {})

    def get_all_state(self) -> dict:
        self._reset_if_new_day()
        return self.state

    def record_click(self, area_key: str, reason: str = ""):
        now = datetime.now(self.tz)
        s = self.state.setdefault(area_key, self._default_state()[area_key])
        s["clicks_today"] += 1
        s["last_click_time"] = now.isoformat()
        s["click_history"].append({"time": now.isoformat(), "reason": reason})
        s["click_history"] = s["click_history"][-200:]
        self._save()
