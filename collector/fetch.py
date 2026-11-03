import json
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def download_json(url, attempts=3):
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (dataset-trenes)"})
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except Exception as error:
            print(f"Intento {attempt} fallido en {url}: {error}", file=sys.stderr)
            if attempt == attempts:
                raise
            time.sleep(5 * attempt)


def now_madrid():
    return datetime.now(MADRID)


def epoch_to_madrid(value):
    if not value:
        return ""
    return datetime.fromtimestamp(int(value), MADRID).isoformat(timespec="seconds")


def require_list(feed, key):
    if not isinstance(feed, dict) or not isinstance(feed.get(key), list):
        raise ValueError(f"Respuesta sin lista '{key}'")
    return feed[key]


def require_rows_in_service_hours(count, now, what):
    if count == 0 and 7 <= now.hour < 23:
        raise ValueError(f"0 {what} en horario de servicio, no se guarda")
