import csv

from fetch import DATA_DIR, download_json, epoch_to_madrid, now_madrid

FEED_URL = "https://gtfsrt.renfe.com/trip_updates_LD.json"
COLUMNS = ["capturado", "tripId", "estado", "retrasoTren", "stopId", "llegadaPrevista", "retrasoLlegada", "salidaPrevista", "retrasoSalida"]


def rows(feed, captured_at):
    for entity in feed.get("entity", []):
        update = entity.get("tripUpdate", {})
        trip = update.get("trip", {})
        base = [captured_at, trip.get("tripId", ""), trip.get("scheduleRelationship", ""), update.get("delay", "")]
        stops = update.get("stopTimeUpdate") or [{}]
        for stop in stops:
            arrival = stop.get("arrival", {})
            departure = stop.get("departure", {})
            yield [*base, stop.get("stopId", ""), epoch_to_madrid(arrival.get("time")), arrival.get("delay", ""), epoch_to_madrid(departure.get("time")), departure.get("delay", "")]


def main():
    now = now_madrid()
    feed = download_json(FEED_URL)
    path = DATA_DIR / "retrasos_ld" / now.strftime("%Y/%m/%d") / f"{now.strftime('%H%M%S')}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(COLUMNS)
        writer.writerows(rows(feed, now.isoformat(timespec="seconds")))
    print(f"{len(feed.get('entity', []))} trenes con retraso oficial guardados en {path.relative_to(DATA_DIR.parent)}")


if __name__ == "__main__":
    main()
