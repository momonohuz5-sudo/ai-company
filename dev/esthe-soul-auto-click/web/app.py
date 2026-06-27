import threading
from datetime import datetime
import pytz
from flask import Flask, render_template, jsonify

from src.config import AREAS, TIMEZONE, WEB_PORT
from src.state_manager import StateManager
from src.rule_engine import RuleEngine

app = Flask(__name__, template_folder="templates")
_state_manager = StateManager()
_rule = RuleEngine()
_tz = pytz.timezone(TIMEZONE)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    now = datetime.now(_tz)
    all_state = _state_manager.get_all_state()
    areas = []

    for area_key, cfg in AREAS.items():
        if not cfg.get("enabled", True):
            continue
        s = all_state.get(area_key, {})
        next_t = _rule.get_next_scheduled_time(s)
        last = s.get("last_click_time")

        areas.append({
            "key": area_key,
            "name": cfg["name"],
            "clicks_today": s.get("clicks_today", 0),
            "remaining": _rule.get_remaining_clicks(s),
            "last_click": datetime.fromisoformat(last).astimezone(_tz).strftime("%H:%M") if last else None,
            "next_click": next_t.strftime("%H:%M") if next_t else None,
            "linked": cfg.get("linked_areas", []),
        })

    return jsonify({
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "areas": areas,
    })


@app.route("/api/history/<area_key>")
def api_history(area_key: str):
    s = _state_manager.get_area_state(area_key)
    history = s.get("click_history", [])
    return jsonify({"history": list(reversed(history[-20:]))})


def start():
    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=WEB_PORT, debug=False),
        daemon=True,
    )
    thread.start()
