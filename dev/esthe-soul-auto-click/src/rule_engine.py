from datetime import datetime, timedelta
import pytz
from src.config import (
    MAX_CLICKS_PER_DAY, MIN_INTERVAL_MINUTES,
    PROHIBITED_START_MINUTE, PROHIBITED_END_MINUTE, PROHIBITED_FALLBACK_MINUTE,
    THIRTY_MINUTE_OVERRIDE_TARGET, THIRTY_MINUTE_OVERRIDE_FALLBACK,
    BEST_BEFORE_EXIT_MINUTES,
    BUSINESS_START_HOUR, BUSINESS_START_MINUTE,
    BUSINESS_END_HOUR, BUSINESS_END_MINUTE,
    TIMEZONE,
)


class RuleEngine:
    def __init__(self):
        self.tz = pytz.timezone(TIMEZONE)

    def is_business_hours(self, now: datetime) -> bool:
        h, m = now.hour, now.minute
        minutes = h * 60 + m
        start = BUSINESS_START_HOUR * 60 + BUSINESS_START_MINUTE  # 600
        end = (BUSINESS_END_HOUR + 24) * 60 + BUSINESS_END_MINUTE  # 1770

        if h < BUSINESS_START_HOUR:
            minutes += 24 * 60
        return start <= minutes <= end

    def is_prohibited_minute(self, minute: int) -> bool:
        return minute >= PROHIBITED_START_MINUTE or minute <= PROHIBITED_END_MINUTE

    def adjust_click_time(self, ideal: datetime) -> datetime:
        m = ideal.minute

        # XX:30 → XX:23
        if m == THIRTY_MINUTE_OVERRIDE_TARGET:
            return ideal.replace(minute=THIRTY_MINUTE_OVERRIDE_FALLBACK, second=0, microsecond=0)

        # 禁止帯 (55〜59) → XX:53 (同時刻の時)
        if m >= PROHIBITED_START_MINUTE:
            return ideal.replace(minute=PROHIBITED_FALLBACK_MINUTE, second=0, microsecond=0)

        # 禁止帯 (00〜10) → 前の時の :53
        if m <= PROHIBITED_END_MINUTE:
            prev_hour = ideal.replace(minute=PROHIBITED_FALLBACK_MINUTE, second=0, microsecond=0) - timedelta(hours=1)
            return prev_hour

        return ideal.replace(second=0, microsecond=0)

    def get_next_scheduled_time(self, area_state: dict) -> datetime | None:
        last = area_state.get("last_click_time")
        if not last:
            return None
        last_dt = datetime.fromisoformat(last).astimezone(self.tz)
        ideal = last_dt + timedelta(minutes=MIN_INTERVAL_MINUTES)
        return self.adjust_click_time(ideal)

    def get_remaining_clicks(self, area_state: dict) -> int:
        return MAX_CLICKS_PER_DAY - area_state.get("clicks_today", 0)

    def should_click_now(
        self,
        area_key: str,
        area_state: dict,
        bookings: dict,
        all_area_bookings: dict,
    ) -> tuple[bool, str]:
        now = datetime.now(self.tz)

        if not self.is_business_hours(now):
            return False, "営業時間外"

        if area_state.get("clicks_today", 0) >= MAX_CLICKS_PER_DAY:
            return False, f"本日上限 ({MAX_CLICKS_PER_DAY}回) 到達"

        last = area_state.get("last_click_time")
        if last:
            elapsed = (now - datetime.fromisoformat(last).astimezone(self.tz)).total_seconds() / 60
            if elapsed < MIN_INTERVAL_MINUTES:
                return False, f"インターバル中 (残り{int(MIN_INTERVAL_MINUTES - elapsed)}分)"

        if self.is_prohibited_minute(now.minute):
            return False, f"禁止時間帯 ({now.minute}分)"

        current_bookings = bookings.get("current", [])
        upcoming_bookings = bookings.get("upcoming", [])

        # 退出15分前チェック（ベストタイミング）
        for bk in current_bookings:
            mins_to_exit = (bk["end"] - now).total_seconds() / 60
            if 0 < mins_to_exit <= BEST_BEFORE_EXIT_MINUTES:
                if not self._next_booking_blocks(bk["end"], upcoming_bookings):
                    return True, f"退出{int(mins_to_exit)}分前（ベストタイミング）"

        # セラピスト受付可否チェック
        if not self._therapist_available(now, current_bookings, upcoming_bookings):
            return False, "直近受付不可（次予約まで時間が少ない）"

        # 他エリア混雑チェック → 推奨
        other_busy = self._other_areas_busy(area_key, all_area_bookings)

        # 定期インターバルタイミングチェック（±1分以内）
        next_time = self.get_next_scheduled_time(area_state)
        if next_time:
            diff = abs((now - next_time).total_seconds())
            if diff <= 60:
                suffix = "（他エリア混雑中）" if other_busy else ""
                return True, f"定期インターバル{suffix}"
            return False, f"次回予定: {next_time.strftime('%H:%M')}"

        # 本日初回: 条件が揃えばすぐクリック
        if other_busy:
            return True, "本日初回（他エリア混雑中）"
        return True, "本日初回"

    def _therapist_available(
        self, now: datetime, current: list, upcoming: list
    ) -> bool:
        if not current and not upcoming:
            return True  # 予約なし = 受付可能

        # 現在の顧客が終わるまでの時間
        if current:
            latest_exit = max(bk["end"] for bk in current)
            mins_to_exit = (latest_exit - now).total_seconds() / 60
            # 退出まで30分以上ある かつ 次予約がすぐ始まる = 受付不可
            if mins_to_exit > 30 and self._next_booking_blocks(latest_exit, upcoming):
                return False

        return True

    def _next_booking_blocks(self, after_time: datetime, upcoming: list) -> bool:
        for bk in upcoming:
            gap = (bk["start"] - after_time).total_seconds() / 60
            if 0 <= gap < 30:
                return True
        return False

    def _other_areas_busy(self, current_area: str, all_bookings: dict) -> bool:
        for area_key, bookings in all_bookings.items():
            if area_key == current_area:
                continue
            if bookings.get("current"):
                return True
        return False
