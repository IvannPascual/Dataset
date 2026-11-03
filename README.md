# Dataset de trenes de larga distancia en España

Capturas periódicas de los trenes de larga distancia y alta velocidad de Renfe, con avisos de incidencias y tiempo meteorológico.

## Cómo se recoge

Un workflow de GitHub Actions (`.github/workflows/renfe.yml`) se ejecuta cada 5 minutos. Lo lanza un Worker de Cloudflare con Cron Trigger por `workflow_dispatch`; el cron propio de GitHub queda como respaldo, porque GitHub retrasa o se salta muchas ejecuciones programadas. Guarda:

| Carpeta | Fuente | Contenido |
|---|---|---|
| `data/renfe/AAAA/MM/DD/HHMMSS.csv` | Mapa de Renfe (`flotaLD.json`) | Posición, retraso y próxima estación de cada tren |
| `data/retrasos_ld/AAAA/MM/DD/HHMMSS.csv` | GTFS-RT oficial de Renfe (`trip_updates_LD.json`) | Retraso por tren y parada, en segundos |
| `data/avisos/AAAA/MM/DD.csv` | GTFS-RT oficial de Renfe (`alerts.json`) | Avisos de incidencias, una fila cada vez que aparece uno nuevo o cambia su texto |
| `data/meteo/AAAA/MM/DD.csv` | Open-Meteo | Temperatura, lluvia, nieve, viento y rachas en 28 puntos de la red, cada 15 minutos |
| `data/estaciones.csv` | Renfe (`estaciones.geojson`) | Código, nombre, coordenadas y provincia de cada estación. Se revisa a diario y solo cambia si Renfe lo cambia |
| `data/horarios/AAAA-MM-DD.zip` | GTFS estático de Renfe AV/LD (`google_transit.zip`) | Horario programado. Se revisa a diario y solo se guarda una versión nueva si cambia su contenido |
| `data/horarios/versiones.csv` | — | Una fila por versión de horarios: fecha, huella SHA-256 del contenido, fichero, viajes y paradas |
| `data/registro/AAAA/MM/DD.csv` | — | Una fila por ejecución de cada colector: estado (`ok`/`error`), filas, fichero, huella SHA-256 y detalle del error |
| `data/festivos/AAAA.csv` | Nager.Date | Festivos nacionales y autonómicos (`comunidades` con códigos ES-XX) del año actual y el siguiente |

## Columnas de `data/renfe`

| Columna | Significado |
|---|---|
| capturado | Hora de la captura (Europe/Madrid) |
| fechaActualizacion | Hora de actualización que indica el feed |
| codComercial | Número de tren |
| codProduct | Código de producto (AVE, Alvia, MD…) |
| codOrigen / codDestino | Estaciones de origen y destino |
| codEstAnt / codEstSig | Estación anterior y siguiente |
| horaLlegadaSigEst | Llegada prevista a la siguiente estación |
| ultRetraso | Último retraso conocido, en minutos |
| latitud / longitud | Posición GPS |
| time | Hora de la posición (epoch, segundos) |
| mat | Material (composición) |
| p | Campo sin documentar del feed |
| accesible | Tren accesible |

Los códigos de estación se traducen con `data/estaciones.csv`.

## Garantías de los datos

- Antes de escribir, cada colector valida la respuesta: estructura esperada, número de puntos, columnas del GTFS. Si no cuadra, no se guarda nada y queda un `error` en `data/registro`.
- Un feed de trenes vacío entre las 07:00 y las 23:00 (Madrid) se trata como error. De noche se guarda vacío, porque no circulan trenes.
- `retrasos_ld` elimina las filas idénticas que el feed repite (trenes cancelados).
- Los huecos se miden con `data/registro`: si una franja no tiene filas `ok`, no hay datos de esa franja.
- Los `tripId` de `retrasos_ld` coinciden con los `trip_id` del GTFS vigente ese día (consultar `versiones.csv`).
- En `avisos` cada fichero diario vuelve a anotar los avisos que siguen activos; para contarlos entre días hay que quitar duplicados por `id` y `texto`.

## Variables derivadas

`python analisis/variables.py salida.csv` genera, a partir de los datos en bruto, una fila por tren y captura con día de la semana, hora, festivo nacional y autonómico, puente, trenes en circulación, retraso medio de la red y retraso medio del mismo tren en los 7 días anteriores. No se guardan en el repo: se regeneran siempre igual con los mismos datos.

## Aviso

El feed no es una API oficial y puede cambiar sin aviso. Los datos se publican tal cual, sin garantías.
