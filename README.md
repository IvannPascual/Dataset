# Dataset de trenes de larga distancia en España

Capturas periódicas de los trenes de larga distancia y alta velocidad de Renfe, con avisos de incidencias y tiempo meteorológico.

## Cómo se recoge

Un workflow de GitHub Actions (`.github/workflows/renfe.yml`) se ejecuta cada 5 minutos (GitHub puede retrasarlo o saltarse alguna ejecución) y guarda:

| Carpeta | Fuente | Contenido |
|---|---|---|
| `data/renfe/AAAA/MM/DD/HHMMSS.csv` | Mapa de Renfe (`flotaLD.json`) | Posición, retraso y próxima estación de cada tren |
| `data/retrasos_ld/AAAA/MM/DD/HHMMSS.csv` | GTFS-RT oficial de Renfe (`trip_updates_LD.json`) | Retraso por tren y parada, en segundos |
| `data/avisos/AAAA/MM/DD.csv` | GTFS-RT oficial de Renfe (`alerts.json`) | Avisos de incidencias, una fila cada vez que aparece uno nuevo o cambia su texto |
| `data/meteo/AAAA/MM/DD.csv` | Open-Meteo | Temperatura, lluvia, nieve, viento y rachas en 28 puntos de la red, cada 15 minutos |
| `data/estaciones.csv` | Renfe (`estaciones.geojson`) | Código, nombre, coordenadas y provincia de cada estación. Se revisa a diario y solo cambia si Renfe lo cambia |
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

## Aviso

El feed no es una API oficial y puede cambiar sin aviso. Los datos se publican tal cual, sin garantías.
