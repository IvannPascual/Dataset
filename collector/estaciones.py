import csv
import io

from fetch import DATA_DIR, download_json, require_list

FEED_URL = "https://tiempo-real.largorecorrido.renfe.com/data/estaciones.geojson"
FIELDS = ["CODIGO", "NOMBRE", "LAT", "LON", "LOCALIDAD", "PROV", "DIR", "ACCESIBLE", "CERC", "NIVEL", "ATENDO"]


def main():
    feed = download_json(FEED_URL)
    stations = sorted((f.get("properties", {}) for f in require_list(feed, "features")), key=lambda p: int(p.get("CODIGO") or 0))
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow([field.lower() for field in FIELDS])
    for station in stations:
        writer.writerow([station.get(field, "") for field in FIELDS])
    if len(stations) < 100:
        raise ValueError(f"Solo {len(stations)} estaciones, no se guarda")
    path = DATA_DIR / "estaciones.csv"
    content = buffer.getvalue()
    if path.exists() and path.read_text(encoding="utf-8") == content:
        print(f"{len(stations)} estaciones, sin cambios")
        return len(stations), None
    path.write_text(content, encoding="utf-8")
    print(f"{len(stations)} estaciones guardadas en {path.relative_to(DATA_DIR.parent)}")
    return len(stations), path


if __name__ == "__main__":
    main()
