import csv
import hashlib
import io
import sys
import time
import urllib.request
import zipfile

from fetch import DATA_DIR, now_madrid

FEED_URL = "https://ssl.renfe.com/gtransit/Fichero_AV_LD/google_transit.zip"
REQUIRED = {
    "agency.txt": {"agency_id"},
    "routes.txt": {"route_id"},
    "trips.txt": {"route_id", "service_id", "trip_id"},
    "stops.txt": {"stop_id", "stop_name"},
    "stop_times.txt": {"trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"},
    "calendar.txt": {"service_id", "start_date", "end_date"},
}
DIR = DATA_DIR / "horarios"
VERSIONS = DIR / "versiones.csv"
COLUMNS = ["descargado", "huella", "fichero", "viajes", "paradas"]


def download(attempts=3):
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0 (dataset-trenes)"})
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except Exception as error:
            print(f"Intento {attempt} fallido en {FEED_URL}: {error}", file=sys.stderr)
            if attempt == attempts:
                raise
            time.sleep(5 * attempt)


def read_table(archive, name):
    text = archive.read(name).decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    header = [h.strip() for h in rows[0]] if rows else []
    return header, rows[1:]


def validate(archive):
    counts = {}
    for name, columns in REQUIRED.items():
        if name not in archive.namelist():
            raise ValueError(f"Falta {name} en el GTFS")
        header, rows = read_table(archive, name)
        missing = columns - set(header)
        if missing:
            raise ValueError(f"{name} sin columnas {sorted(missing)}")
        if not rows:
            raise ValueError(f"{name} vacío")
        counts[name] = len(rows)
    return counts


def content_hash(archive):
    digest = hashlib.sha256()
    for name in sorted(archive.namelist()):
        digest.update(name.encode())
        digest.update(archive.read(name))
    return digest.hexdigest()


def last_hash():
    if not VERSIONS.exists():
        return None
    with VERSIONS.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    return rows[-1]["huella"] if rows else None


def main():
    now = now_madrid()
    raw = download()
    archive = zipfile.ZipFile(io.BytesIO(raw))
    counts = validate(archive)
    digest = content_hash(archive)
    if digest == last_hash():
        print(f"Horarios sin cambios ({counts['trips.txt']} viajes)")
        return counts["trips.txt"], None
    path = DIR / f"{now.strftime('%Y-%m-%d')}.zip"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    is_new_file = not VERSIONS.exists()
    with VERSIONS.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        if is_new_file:
            writer.writerow(COLUMNS)
        writer.writerow([now.isoformat(timespec="seconds"), digest, path.name, counts["trips.txt"], counts["stop_times.txt"]])
    print(f"Nueva versión de horarios: {counts['trips.txt']} viajes en {path.relative_to(DATA_DIR.parent)}")
    return counts["trips.txt"], path


if __name__ == "__main__":
    main()
