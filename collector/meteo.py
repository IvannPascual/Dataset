import csv

from fetch import DATA_DIR, download_json, now_madrid

POINTS = {
    "Madrid": (40.406, -3.690),
    "Guadalajara": (40.590, -3.150),
    "Zaragoza": (41.658, -0.911),
    "Lleida": (41.620, 0.633),
    "Tarragona": (41.192, 1.169),
    "Barcelona": (41.379, 2.140),
    "Cuenca": (40.035, -2.142),
    "Valencia": (39.459, -0.383),
    "Albacete": (38.985, -1.857),
    "Alicante": (38.344, -0.495),
    "Ciudad Real": (38.995, -3.913),
    "Urda": (39.410, -3.720),
    "Puertollano": (38.684, -4.108),
    "Cordoba": (37.889, -4.789),
    "Sevilla": (37.392, -5.975),
    "Antequera": (37.010, -4.560),
    "Malaga": (36.712, -4.432),
    "Segovia": (40.910, -4.097),
    "Valladolid": (41.643, -4.729),
    "Palencia": (42.012, -4.535),
    "Leon": (42.596, -5.578),
    "Burgos": (42.343, -3.682),
    "Miranda de Ebro": (42.683, -2.940),
    "Zamora": (41.512, -5.735),
    "Ourense": (42.340, -7.860),
    "Santiago": (42.871, -8.545),
    "Badajoz": (38.886, -6.975),
    "Pamplona": (42.800, -1.666),
}
VARIABLES = ["temperature_2m", "precipitation", "rain", "snowfall", "wind_speed_10m", "wind_gusts_10m", "weather_code"]
COLUMNS = ["capturado", "punto", "latitud", "longitud", "horaDato", *VARIABLES]


def main():
    now = now_madrid()
    names = list(POINTS)
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={','.join(str(POINTS[n][0]) for n in names)}"
        f"&longitude={','.join(str(POINTS[n][1]) for n in names)}"
        f"&current={','.join(VARIABLES)}&timezone=Europe%2FMadrid"
    )
    results = download_json(url)
    path = DATA_DIR / "meteo" / now.strftime("%Y/%m") / f"{now.strftime('%d')}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(COLUMNS)
        for name, result in zip(names, results):
            current = result.get("current", {})
            writer.writerow([now.isoformat(timespec="seconds"), name, *POINTS[name], current.get("time", ""), *(current.get(v, "") for v in VARIABLES)])
    print(f"Tiempo guardado para {len(names)} puntos")


if __name__ == "__main__":
    main()
