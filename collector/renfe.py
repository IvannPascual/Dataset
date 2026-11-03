import csv
import io
import json
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fetch import require_list, require_rows_in_service_hours

FEED_URL = "https://tiempo-real.largorecorrido.renfe.com/renfe-visor/flotaLD.json"
MADRID = ZoneInfo("Europe/Madrid")
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "renfe"
FIELDS = [
    "codComercial",
    "codProduct",
    "codOrigen",
    "codDestino",
    "codEstAnt",
    "codEstSig",
    "horaLlegadaSigEst",
    "ultRetraso",
    "latitud",
    "longitud",
    "time",
    "mat",
    "p",
    "accesible",
]
COLUMNS = ["capturado", "fechaActualizacion", *FIELDS]


def download_feed(attempts=3):
    for attempt in range(1, attempts + 1):
        try:
            url = f"{FEED_URL}?v={int(time.time() * 1000)}"
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (dataset-trenes)"})
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except Exception as error:
            print(f"Intento {attempt} fallido: {error}", file=sys.stderr)
            if attempt == attempts:
                raise
            time.sleep(5 * attempt)


def to_csv(feed, captured_at):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(COLUMNS)
    for train in feed.get("trenes", []):
        writer.writerow([captured_at, feed.get("fechaActualizacion", ""), *(train.get(field, "") for field in FIELDS)])
    return buffer.getvalue()


def main():
    now = datetime.now(MADRID)
    feed = download_feed()
    trains = len(require_list(feed, "trenes"))
    require_rows_in_service_hours(trains, now, "trenes")
    path = DATA_DIR / now.strftime("%Y/%m/%d") / f"{now.strftime('%H%M%S')}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_csv(feed, now.isoformat(timespec="seconds")), encoding="utf-8")
    print(f"{trains} trenes guardados en {path.relative_to(DATA_DIR.parent.parent)}")
    return trains, path


if __name__ == "__main__":
    main()
