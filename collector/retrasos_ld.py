import csv

from fetch import DATA_DIR, download_json, epoch_to_madrid, now_madrid, require_list, require_rows_in_service_hours

FEED_URL = "https://gtfsrt.renfe.com/trip_updates_LD.json"
COLUMNS = ["capturado", "tripId", "estado", "retrasoTren", "stopId", "llegadaPrevista", "retrasoLlegada", "salidaPrevista", "retrasoSalida"]


def rows(feed, captured_at):
    seen = set()
    for entity in feed["entity"]:
        update = entity.get("tripUpdate", {})
        trip = update.get("trip", {})
        base = [captured_at, trip.get("tripId", ""), trip.get("scheduleRelationship", ""), update.get("delay", "")]
        stops = update.get("stopTimeUpdate") or [{}]
        for stop in stops:
            arrival = stop.get("arrival", {})
            departure = stop.get("departure", {})
            row = (*base, stop.get("stopId", ""), epoch_to_madrid(arrival.get("time")), arrival.get("delay", ""), epoch_to_madrid(departure.get("time")), departure.get("delay", ""))
            if row not in seen:
                seen.add(row)
                yield row


def main():
    now = now_madrid()
    feed = download_json(FEED_URL)
    trains = len(require_list(feed, "entity"))
    require_rows_in_service_hours(trains, now, "trenes")
    output = list(rows(feed, now.isoformat(timespec="seconds")))
    path = DATA_DIR / "retrasos_ld" / now.strftime("%Y/%m/%d") / f"{now.strftime('%H%M%S')}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(COLUMNS)
        writer.writerows(output)
    print(f"{trains} trenes con retraso oficial guardados en {path.relative_to(DATA_DIR.parent)}")
    return len(output), path


if __name__ == "__main__":
    main()
