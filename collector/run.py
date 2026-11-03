import csv
import hashlib
import importlib
import sys
import traceback

from fetch import DATA_DIR, now_madrid

COLUMNS = ["ejecutado", "fuente", "estado", "filas", "fichero", "huella", "detalle"]


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path and path.exists() else ""


def log(source, status, rows, path, detail):
    now = now_madrid()
    log_path = DATA_DIR / "registro" / now.strftime("%Y/%m") / f"{now.strftime('%d')}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        if is_new_file:
            writer.writerow(COLUMNS)
        relative = str(path.relative_to(DATA_DIR.parent)) if path else ""
        writer.writerow([now.isoformat(timespec="seconds"), source, status, rows, relative, file_hash(path), detail[:300]])


def main():
    source = sys.argv[1]
    try:
        rows, path = importlib.import_module(source).main()
    except Exception as error:
        traceback.print_exc()
        log(source, "error", "", None, f"{type(error).__name__}: {error}")
        sys.exit(1)
    log(source, "ok", rows, path, "")


if __name__ == "__main__":
    main()
