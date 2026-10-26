import csv
import json
import random

import hashlib
from pathlib import Path
from datetime import time

carpeta_base = Path(__file__).resolve().parent
ruta_csv = carpeta_base / "output" / "age_citas.csv"

total = 0
especialidades_nulas = 0
atendidas_sin_horas = 0
no_atendidas_con_horas = 0
esperas_negativas = 0

estados = {
    "Atendida": 0,
    "Cancelada": 0,
    "No asistió": 0
}

with open(ruta_csv, newline="", encoding="utf-8") as archivo:
    lector = csv.DictReader(archivo)

    for fila in lector:
        total += 1

        if fila["esp_solicitada"] == "":
            especialidades_nulas += 1

        estado = fila["estado_cita"]
        estados[estado] += 1

        llegada = fila["hra_llegada_paciente"]
        inicio = fila["hra_inicio_atencion"]

        if estado == "Atendida":
            if llegada == "" or inicio == "":
                atendidas_sin_horas += 1
            else:
                if time.fromisoformat(inicio) < time.fromisoformat(llegada):
                    esperas_negativas += 1
        else:
            if llegada != "" or inicio != "":
                no_atendidas_con_horas += 1

print(f"Total: {total}")
print(f"Especialidades nulas: {especialidades_nulas}")
print(f"Atendidas sin horas: {atendidas_sin_horas}")
print(f"No atendidas con horas: {no_atendidas_con_horas}")
print(f"Esperas negativas: {esperas_negativas}")

for estado, cantidad in estados.items():
    print(f"{estado}: {cantidad}")

