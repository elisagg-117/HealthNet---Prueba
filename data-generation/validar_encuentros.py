# Leemos la muestra y reportamos los reusltados.
import csv
import json
import random

import hashlib
from pathlib import Path
from datetime import date, datetime, timedelta

carpeta_base = Path(__file__).resolve().parent

with open(carpeta_base / "config.json", encoding="utf-8-sig") as archivo:
    config = json.load(archivo)

inicio = datetime.fromisoformat(config["fecha_inicio"])
fin = (datetime.fromisoformat(config["fecha_fin"]) + timedelta(days=1, seconds=-1))

ruta_csv = carpeta_base / "output" / "hce_encuentros.csv"

total = 0
duplicados = 0
fechas_inconsistentes = 0
fuera_periodo = 0
importes_invalidos = 0

identificadores = set()
meses = set()

with open(ruta_csv, newline="", encoding="utf-8") as archivo:
    lector = csv.DictReader(archivo)

    for registro in lector:
        total += 1

        identificador = registro["id_encuentro"]

        if identificador in identificadores:
            duplicados += 1

        identificadores.add(identificador)

        fec_registro = datetime.fromisoformat(
            registro["fec_registro"]
        )
        fec_inicio = datetime.fromisoformat(
            registro["fec_inicio_atencion"]
        )
        fec_egreso = datetime.fromisoformat(
            registro["fec_egreso"]
        )

        if not fec_registro <= fec_inicio <= fec_egreso:
            fechas_inconsistentes += 1

        if not inicio <= fec_registro < fin:
            fuera_periodo += 1

        if float(registro["vr_facturado"]) <= 0:
            importes_invalidos += 1

        meses.add(fec_registro.strftime("%Y-%m"))

print(f"Total: {total}")
print(f"Identificadores duplicados: {duplicados}")
print(f"Fechas inconsistentes: {fechas_inconsistentes}")
print(f"Fuera del período: {fuera_periodo}")
print(f"Importes inválidos: {importes_invalidos}")
print(f"Meses representados: {len(meses)}")