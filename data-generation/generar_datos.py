import csv
import json
import random

import hashlib
from pathlib import Path
from datetime import date, timedelta

# Localizamos la configuración junto a este script.
carpeta_base = Path(__file__).resolve().parent

with open(carpeta_base / "config.json", encoding="utf-8-sig") as archivo:
    config = json.load(archivo)

aleatorio = random.Random(config["semilla"])

carpeta_salida = carpeta_base / "output"
carpeta_salida.mkdir(parents=True, exist_ok=True)


# Catálogos iniciales de las tablas aux creadas en la bd.
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


# Generamos las sedes respetando las cantidades configuradas (82).
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
            # Para esta simulación, los centros son ambulatorios (es decir, que el paciente puede recibir atencion sin ocupar ser hospitalizado)
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

# Armado de medicos.
fecha_inicio = date.fromisoformat(config["fecha_inicio"])
especialidades = [
    "Medicina general",
    "Medicina interna",
    "Pediatría",
    "Cardiología",
    "Ginecología",
    "Ortopedia"
]
medicos = []

for id_med in range(1, config["cantidad_medicos"] + 1):
    sede = aleatorio.choice(sedes)
    # definición de % de probabilidad para especialidades apareciendo unas mas que otraas como medicina general.
    esp_principal = aleatorio.choices(
        especialidades,
        weights=[40, 15, 15, 10, 10, 10],
        k=1
    )[0]

    esp_secundaria = None
    # dDefinimos que aprox. el 20% tendra una especialidad secundaria o eso se espera.
    if aleatorio.random() < 0.20:
        opciones_secundarias = [
            especialidad
            for especialidad in especialidades
            # evitamos que se repita la especialidad.
            if especialidad != esp_principal
        ]
        esp_secundaria = aleatorio.choice(opciones_secundarias)
    # El ingreso debe quedar entre la fecha de inicio configurada en los param y 10 años antes
    fec_ingreso = fecha_inicio - timedelta(
        days=aleatorio.randint(0, 3650)
    )

    medico = {
        "id_med": id_med,
        "esp_principal": esp_principal,
        "esp_secundaria": esp_secundaria,
        "sede_id": sede["id_sede"],
        "fec_ingreso": fec_ingreso.isoformat(),
        "tip_contrato": aleatorio.choice([
            "Indefinido",
            "Temporal",
            "Prestación de servicios"
        ]),
        "jornada": aleatorio.choice(["Completa", "Parcial"]),
        "estado_activo": True
    }

    medicos.append(medico)


# Armado de pacientes
aseguradoras = []

for id_eps in range(1, 43):
    aseguradora = {
        "id_eps": id_eps,
        "tip_aseguradora": aleatorio.choice([
            "Pública",
            "Privada",
            "Mixta"
        ])
    }

    aseguradoras.append(aseguradora)

pacientes = []

for id_pac in range(1, config["cantidad_pacientes"] + 1):
    ciudad = aleatorio.choice(ciudades)
    aseguradora = aleatorio.choice(aseguradoras)

    edad = aleatorio.gauss(
        config["edad_media"],
        config["edad_desviacion"]
    )

    while edad < 0 or edad > config["edad_maxima"]:
        edad = aleatorio.gauss(
            config["edad_media"],
            config["edad_desviacion"]
        )

    fec_nac = fecha_inicio - timedelta(days=int(edad * 365.25))

    antiguedad_maxima = min(3650,(fecha_inicio - fec_nac).days)

    fec_primer_atencion = fecha_inicio - timedelta(days=aleatorio.randint(0, antiguedad_maxima))

    edad_calendario = fecha_inicio.year - fec_nac.year

    if (fecha_inicio.month, fecha_inicio.day) < (fec_nac.month,fec_nac.day):
        edad_calendario -= 1

    if ciudad["pais_id"] == 1:
        if edad_calendario < 7:
            #tipo doc: registro civil
            tip_doc = "RC"
        elif edad_calendario < 18:
            #tipo doc: tarjeta de identificacion
            tip_doc = "TI"
        else:
            #tipo doc: cedula de ciudadania
            tip_doc = "CC"
    elif ciudad["pais_id"] == 2:
        #tipo doc: documento nacional de identidad
        tip_doc = "DNI"
    else:
        #tipo doc: cedula
        tip_doc = "CED"

    documento_sintetico = f"HealthNet-{id_pac}"

    num_doc_hash = hashlib.sha256(
        documento_sintetico.encode("utf-8")
    ).hexdigest()

    paciente = {
        "id_pac": id_pac,
        "tip_doc": tip_doc,
        "num_doc_hash": num_doc_hash,
        "fec_nac": fec_nac.isoformat(),
        "genero": aleatorio.choice(["F", "M"]),
        "ciudad_res_id": ciudad["id_ciudad"],
        "tip_aseguradora": aseguradora["tip_aseguradora"],
        "id_eps": aseguradora["id_eps"],
        "estrato_socioec": aleatorio.randint(1, 6),
        "fec_primer_atencion": fec_primer_atencion.isoformat(),
        "activo": True
    }

    pacientes.append(paciente)

# Construcction de archivos con datos generados.
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

# Exportacion de archivos egenrados.
guardar_archivos("cat_pais", paises, carpeta_salida)
guardar_archivos("cat_ciudad", ciudades, carpeta_salida)
guardar_archivos("red_sedes", sedes, carpeta_salida)
guardar_archivos("med_planta", medicos, carpeta_salida)
guardar_archivos("pac_registro", pacientes, carpeta_salida)

print(f"\nArchivos guardados en: {carpeta_salida}")