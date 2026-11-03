import csv

from fetch import DATA_DIR, download_json, epoch_to_madrid, now_madrid, require_list

FEED_URL = "https://gtfsrt.renfe.com/alerts.json"
COLUMNS = ["visto", "id", "inicio", "fin", "rutas", "texto"]


def alert_text(alert):
    translations = alert.get("descriptionText", {}).get("translation", [])
    spanish = [t["text"] for t in translations if t.get("language") == "es"]
    return (spanish or [t.get("text", "") for t in translations] or [""])[0].strip()


def main():
    now = now_madrid()
    feed = download_json(FEED_URL)
    require_list(feed, "entity")
    path = DATA_DIR / "avisos" / now.strftime("%Y/%m") / f"{now.strftime('%d')}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    if path.exists():
        with path.open(newline="", encoding="utf-8") as file:
            seen = {(row["id"], row["texto"]) for row in csv.DictReader(file)}
    new_rows = []
    for entity in feed.get("entity", []):
        alert = entity.get("alert", {})
        text = alert_text(alert)
        if (entity.get("id", ""), text) in seen:
            continue
        period = (alert.get("activePeriod") or [{}])[0]
        routes = sorted({e.get("routeId", "") for e in alert.get("informedEntity", []) if e.get("routeId")})
        new_rows.append([now.isoformat(timespec="seconds"), entity.get("id", ""), epoch_to_madrid(period.get("start")), epoch_to_madrid(period.get("end")), " ".join(routes), text])
    is_new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(COLUMNS)
        writer.writerows(new_rows)
    print(f"{len(new_rows)} avisos nuevos de {len(feed.get('entity', []))} activos")
    return len(new_rows), path


if __name__ == "__main__":
    main()
