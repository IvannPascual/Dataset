"""Genera variables derivadas a partir de data/renfe y data/festivos.

Uso: python analisis/variables.py salida.csv

Una fila por tren y captura. Se recalcula siempre desde los datos en bruto,
así que el resultado es el mismo para los mismos datos de entrada.
"""

import csv
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DAYS = 7
COLUMNS = [
    "capturado",
    "codComercial",
    "codProduct",
    "ultRetraso",
    "diaSemana",
    "hora",
    "festivoNacional",
    "festivosAutonomicos",
    "puente",
    "trenesEnCirculacion",
    "retrasoMedioRed",
    "retrasoMedioTren7d",
    "capturasTren7d",
]


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_holidays():
    national, regional = set(), defaultdict(list)
    for path in sorted((DATA_DIR / "festivos").glob("*.csv")):
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                day = date.fromisoformat(row["fecha"])
                if row["nacional"] == "si":
                    national.add(day)
                else:
                    regional[day].extend(row["comunidades"].split())
    return national, regional


def is_bridge(day, national):
    if day.weekday() >= 5 or day in national:
        return False
    if day.weekday() == 0 and day + timedelta(days=1) in national:
        return True
    return day.weekday() == 4 and day - timedelta(days=1) in national


def captures():
    for path in sorted((DATA_DIR / "renfe").glob("*/*/*/*.csv")):
        with path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        if rows:
            yield datetime.fromisoformat(rows[0]["capturado"]), rows


def daily_train_delays():
    totals = defaultdict(lambda: [0.0, 0])
    for captured, rows in captures():
        for row in rows:
            delay = number(row["ultRetraso"])
            if delay is not None:
                total = totals[(captured.date(), row["codComercial"])]
                total[0] += delay
                total[1] += 1
    return totals


def main():
    output = Path(sys.argv[1])
    national, regional = load_holidays()
    totals = daily_train_delays()
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(COLUMNS)
        for captured, rows in captures():
            day = captured.date()
            delays = [d for d in (number(r["ultRetraso"]) for r in rows) if d is not None]
            network = round(sum(delays) / len(delays), 2) if delays else ""
            for row in rows:
                history = [totals.get((day - timedelta(days=n), row["codComercial"])) for n in range(1, DAYS + 1)]
                history = [h for h in history if h]
                delay_sum, count = sum(h[0] for h in history), sum(h[1] for h in history)
                writer.writerow([
                    row["capturado"],
                    row["codComercial"],
                    row["codProduct"],
                    row["ultRetraso"],
                    day.isoweekday(),
                    captured.hour,
                    "si" if day in national else "no",
                    " ".join(sorted(set(regional.get(day, [])))),
                    "si" if is_bridge(day, national) else "no",
                    len(rows),
                    network,
                    round(delay_sum / count, 2) if count else "",
                    count,
                ])
    print(f"Variables guardadas en {output}")


if __name__ == "__main__":
    main()
