import os
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

_CONFIG = load_config()

BROWSER = _CONFIG.get("browser", "chrome")
HEADLESS = _CONFIG.get("headless", False)
IMPLICIT_WAIT = _CONFIG.get("implicit_wait", 10)
EXPLICIT_WAIT = _CONFIG.get("explicit_wait", 15)
BASE_URL = _CONFIG.get("base_url", "https://www.redbus.in")
DEFAULT_SEARCH = _CONFIG.get("default_search", {
    "source": "Bangalore",
    "destination": "Chennai",
    "days_ahead": 1,
    "bus_type": "AC"
})
PASSENGER_DATA = _CONFIG.get("passenger", {
    "name": "Ranjith Kumar",
    "gender": "Male",
    "age": 24,
    "email": "ranjith.test@example.com",
    "phone": "9876543210"
})
AI_SETTINGS = _CONFIG.get("ai_settings", {
    "budget_limit": 1500,
    "preferred_time": "evening",
    "min_rating": 4.0
})
REPORTS_DIR = BASE_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

