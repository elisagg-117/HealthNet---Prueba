import csv
import json
import random
from pathlib import Path


# Localizamos la configuración junto a este script.
carpeta_base = Path(__file__).resolve().parent

with open(carpeta_base / "config.json", encoding="utf-8-sig") as archivo:
    config = json.load(archivo)

aleatorio = random.Random(config["semilla"])

carpeta_salida = carpeta_base / "output"
carpeta_salida.mkdir(parents=True, exist_ok=True)


# Catálogos iniciales.
paises = [
    {"id_pais": 1, "nom_pais": "Colombia"},
    {"id_pais": 2, "nom_pais": "Perú"},
    {"id_pais": 3, "nom_pais": "Ecuador"}
]

ciudades = [
    {"id_ciudad": 1, "nom_ciudad": "Bogotá", "pais_id": 1},
    {"id_ciudad": 2, "nom_ciudad": "Medellín", "pais_id": 1},
    {"id_ciudad": 3, "nom_ciudad": "Cali", "pais_id": 1},
    {"id_ciudad": 4, "nom_ciudad": "Lima", "pais_id": 2},
    {"id_ciudad": 5, "nom_ciudad": "Arequipa", "pais_id": 2},
    {"id_ciudad": 6, "nom_ciudad": "Cusco", "pais_id": 2},
    {"id_ciudad": 7, "nom_ciudad": "Quito", "pais_id": 3},
    {"id_ciudad": 8, "nom_ciudad": "Guayaquil", "pais_id": 3},
    {"id_ciudad": 9, "nom_ciudad": "Cuenca", "pais_id": 3}
]


# Generamos las sedes respetando las cantidades configuradas.
sedes = []

for tipo, cantidad in config["sedes_por_tipo"].items():

    for numero in range(cantidad):
        ciudad = aleatorio.choice(ciudades)

        if tipo == "hospital":
            camas_gen = aleatorio.randint(80, 200)
            camas_uci = aleatorio.randint(10, 30)
            camas_cirugia = aleatorio.randint(4, 12)
            camas_urg = aleatorio.randint(10, 30)
            nivel = "Alta"

        elif tipo == "clinica":
            camas_gen = aleatorio.randint(10, 50)
            camas_uci = aleatorio.randint(0, 6)
            camas_cirugia = aleatorio.randint(1, 6)
            camas_urg = aleatorio.randint(2, 10)
            nivel = "Media"

        else:
            # Para esta simulación, los centros son ambulatorios.
            camas_gen = 0
            camas_uci = 0
            camas_cirugia = 0
            camas_urg = 0
            nivel = "Baja"

        id_sede = len(sedes) + 1

        sede = {
            "id_sede": id_sede,
            "nom_sede": f"Sede HealthNet {id_sede}",
            "tip_sede": tipo,
            "ciudad_id": ciudad["id_ciudad"],
            "pais_id": ciudad["pais_id"],
            "cap_camas_gen": camas_gen,
            "cap_camas_uci": camas_uci,
            "cap_camas_cirugia": camas_cirugia,
            "cap_camas_urg": camas_urg,
            "nivel_complejidad": nivel
        }

        sedes.append(sede)


# Reutilizamos la misma función para exportar cada tabla.
def guardar_archivos(tabla, registros, carpeta):

    campos = list(registros[0].keys())

    with open(
        carpeta / f"{tabla}.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(registros)

    with open(
        carpeta / f"{tabla}.json",
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(registros, archivo, ensure_ascii=False, indent=2)

    print(f"{tabla}: {len(registros)} registros, CSV y JSON")


guardar_archivos("cat_pais", paises, carpeta_salida)
guardar_archivos("cat_ciudad", ciudades, carpeta_salida)
guardar_archivos("red_sedes", sedes, carpeta_salida)

print(f"\nArchivos guardados en: {carpeta_salida}")