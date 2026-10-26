import csv
import json
import random

import hashlib
from pathlib import Path
from datetime import date, datetime, timedelta

carpeta_base = Path(__file__).resolve().parent
ruta_csv = carpeta_base / "output" / "far_dispensacion_muestra.csv"

identificadores = set()
datos_encontrados = set()

total = 0
identificadores_duplicados = 0
duplicados_negocio = 0

with open(ruta_csv, newline="", encoding="utf-8") as archivo:
    lector = csv.DictReader(archivo)

    for fila in lector:
        total += 1

        identificador = fila["id_dispensacion"]

        if identificador in identificadores:
            identificadores_duplicados += 1

        identificadores.add(identificador)

        datos_negocio = tuple(
            fila[campo]
            for campo in lector.fieldnames
            if campo != "id_dispensacion"
        )

        if datos_negocio in datos_encontrados:
            duplicados_negocio += 1

        datos_encontrados.add(datos_negocio)

print(f"Total: {total}")
print(f"Identificadores duplicados: {identificadores_duplicados}")
print(f"Duplicados de negocio: {duplicados_negocio}")
print(f"Combinaciones de negocio distintas: {len(datos_encontrados)}")