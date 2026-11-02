import csv
import io

from fetch import DATA_DIR, download_json, now_madrid

API_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/ES"
COLUMNS = ["fecha", "nombre", "nacional", "comunidades"]


def main():
    year = now_madrid().year
    for target in (year, year + 1):
        holidays = download_json(API_URL.format(year=target))
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(COLUMNS)
        for holiday in holidays:
            regions = " ".join(holiday.get("counties") or [])
            writer.writerow([holiday.get("date", ""), holiday.get("localName", ""), "si" if holiday.get("global") else "no", regions])
        path = DATA_DIR / "festivos" / f"{target}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        content = buffer.getvalue()
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
        print(f"{len(holidays)} festivos de {target}")


if __name__ == "__main__":
    main()
