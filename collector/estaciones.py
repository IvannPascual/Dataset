import csv
import io

from fetch import DATA_DIR, download_json

FEED_URL = "https://tiempo-real.largorecorrido.renfe.com/data/estaciones.geojson"
FIELDS = ["CODIGO", "NOMBRE", "LAT", "LON", "LOCALIDAD", "PROV", "DIR", "ACCESIBLE", "CERC", "NIVEL", "ATENDO"]


def main():
    feed = download_json(FEED_URL)
    stations = sorted((f.get("properties", {}) for f in feed.get("features", [])), key=lambda p: int(p.get("CODIGO") or 0))
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow([field.lower() for field in FIELDS])
    for station in stations:
        writer.writerow([station.get(field, "") for field in FIELDS])
    path = DATA_DIR / "estaciones.csv"
    content = buffer.getvalue()
    if path.exists() and path.read_text(encoding="utf-8") == content:
        print(f"{len(stations)} estaciones, sin cambios")
        return
    path.write_text(content, encoding="utf-8")
    print(f"{len(stations)} estaciones guardadas en {path.relative_to(DATA_DIR.parent)}")


if __name__ == "__main__":
    main()
