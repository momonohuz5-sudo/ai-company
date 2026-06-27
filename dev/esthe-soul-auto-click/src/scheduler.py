import asyncio
import logging
from datetime import datetime
import pytz

from src.config import AREAS, CALENDAR_REFRESH_MINUTES, TIMEZONE
from src.calendar_client import CalendarClient
from src.esthe_client import EstheClient
from src.rule_engine import RuleEngine
from src.state_manager import StateManager

logger = logging.getLogger(__name__)


class AutoPochiScheduler:
    def __init__(self):
        self.tz = pytz.timezone(TIMEZONE)
        self.rule = RuleEngine()
        self.state = StateManager()
        self.calendar = CalendarClient()
        self.esthe = EstheClient()
        self._all_bookings: dict = {}
        self._calendar_refreshed_at: datetime | None = None

    async def start(self):
        logger.info("=== 自動ポチシステム 起動 ===")
        await self.esthe.start()
        await self._refresh_calendar()

        try:
            while True:
                await self._cycle()
                await asyncio.sleep(60)
        finally:
            await self.esthe.close()

    async def _refresh_calendar(self):
        logger.info("カレンダー情報を更新中...")
        loop = asyncio.get_event_loop()
        self._all_bookings = await loop.run_in_executor(
            None, self.calendar.get_all_area_bookings
        )
        self._calendar_refreshed_at = datetime.now(self.tz)
        logger.info("カレンダー更新完了")

    async def _cycle(self):
        now = datetime.now(self.tz)

        # カレンダー定期更新
        if (
            self._calendar_refreshed_at is None
            or (now - self._calendar_refreshed_at).total_seconds() > CALENDAR_REFRESH_MINUTES * 60
        ):
            await self._refresh_calendar()

        self.state._reset_if_new_day()

        clicked_this_cycle: set[str] = set()

        for area_key, cfg in AREAS.items():
            if not cfg.get("enabled", True):
                continue
            if area_key in clicked_this_cycle:
                continue

            area_state = self.state.get_area_state(area_key)
            bookings = self._all_bookings.get(area_key, {"current": [], "upcoming": []})

            ok, reason = self.rule.should_click_now(
                area_key, area_state, bookings, self._all_bookings
            )

            if not ok:
                logger.debug(f"{cfg['name']}: スキップ ({reason})")
                continue

            # クリック対象: このエリア + 連動エリア
            targets = list(set([area_key] + cfg.get("linked_areas", [])))

            for target in targets:
                if target in clicked_this_cycle:
                    continue
                target_cfg = AREAS.get(target, {})
                if not target_cfg.get("enabled", True):
                    continue

                t_state = self.state.get_area_state(target)
                if t_state.get("clicks_today", 0) >= 10:
                    logger.info(f"{target_cfg.get('name', target)}: 本日上限のためスキップ")
                    continue

                logger.info(f"▶ ポチ実行: {target_cfg.get('name', target)} [{reason}]")
                success = await self.esthe.execute_pochi(target)

                if success:
                    self.state.record_click(target, reason)
                    clicked_this_cycle.add(target)
                    remaining = self.rule.get_remaining_clicks(self.state.get_area_state(target))
                    logger.info(
                        f"✓ 完了: {target_cfg.get('name', target)} "
                        f"(本日残り{remaining}回)"
                    )
