import os
import pickle
from datetime import datetime, timedelta
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from src.config import AREAS, TIMEZONE

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_FILE = "credentials/token.pickle"
CREDENTIALS_FILE = "credentials/credentials.json"


class CalendarClient:
    def __init__(self):
        self.tz = pytz.timezone(TIMEZONE)
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            os.makedirs("credentials", exist_ok=True)
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)

        return build("calendar", "v3", credentials=creds)

    def _business_day_range(self, now: datetime) -> tuple[datetime, datetime]:
        if now.hour < 10:
            start = (now - timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        else:
            start = now.replace(hour=10, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=19, minutes=30)  # 翌5:30
        return start, end

    def get_bookings(self, calendar_id: str) -> dict:
        now = datetime.now(self.tz)
        day_start, day_end = self._business_day_range(now)

        result = (
            self.service.events()
            .list(
                calendarId=calendar_id,
                timeMin=day_start.isoformat(),
                timeMax=day_end.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        current, upcoming = [], []
        for ev in result.get("items", []):
            start_str = ev["start"].get("dateTime", ev["start"].get("date"))
            end_str = ev["end"].get("dateTime", ev["end"].get("date"))
            start = datetime.fromisoformat(start_str).astimezone(self.tz)
            end = datetime.fromisoformat(end_str).astimezone(self.tz)

            if start <= now <= end:
                current.append({"start": start, "end": end, "summary": ev.get("summary", "")})
            elif now < start <= now + timedelta(hours=3):
                upcoming.append({"start": start, "end": end, "summary": ev.get("summary", "")})

        return {"current": current, "upcoming": upcoming}

    def get_all_area_bookings(self) -> dict:
        result = {}
        for area_key, cfg in AREAS.items():
            if not cfg.get("enabled", True):
                continue
            cal_id = cfg.get("calendar_id")
            if cal_id:
                try:
                    result[area_key] = self.get_bookings(cal_id)
                except Exception as e:
                    print(f"[CalendarClient] {cfg['name']} 取得エラー: {e}")
                    result[area_key] = {"current": [], "upcoming": []}
            else:
                result[area_key] = {"current": [], "upcoming": []}
        return result
