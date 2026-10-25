import csv
import json
import random

import hashlib
from pathlib import Path
from datetime import date, datetime, timedelta

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

# Armado de info camas y mediciones condsideradas. Se usa una def y yield cambiando la logica de construccion de registros por el volumen minimo, asi se intenta hacer progresivo
def generar_camas():
    unidades = []

    campos_capacidad = [
        ("General", "cap_camas_gen"),
        ("UCI", "cap_camas_uci"),
        ("Cirugía", "cap_camas_cirugia"),
        ("Urgencias", "cap_camas_urg")
    ]

    for sede in sedes:
        for tipo_unidad, campo in campos_capacidad:
            if sede[campo] > 0:
                unidades.append(
                    (sede, tipo_unidad, sede[campo])
                )

    if not unidades:
        raise ValueError("No hay unidades con capacidad de camas.")

    cantidad = config["cantidad_camas"]

    cantidad_anomalias = round(cantidad * config["porcentaje_anomalias"])

    ids_anomalos = set(aleatorio.sample(range(1, cantidad + 1),cantidad_anomalias))

    inicio = datetime.fromisoformat(config["fecha_inicio"])

    fin = (datetime.fromisoformat(config["fecha_fin"]) + timedelta(days=1, seconds=-1))

    segundos_periodo = int((fin - inicio).total_seconds())
    desplazamiento = timedelta(days=(fin - inicio).days + 31)

    for id_registro in range(1, cantidad + 1):
        sede, tipo_unidad, capacidad = unidades[(id_registro - 1) % len(unidades)]

        momento = inicio + timedelta(
            seconds=(
                (id_registro - 1)
                * segundos_periodo
                // max(cantidad - 1, 1)
            )
        )

        if sede["tip_sede"] == "hospital":
            ocupacion_media = 0.85

            if momento.month in config["meses_alta_demanda"]:
                ocupacion_media = 0.95
        else:
            ocupacion_media = 0.70

        proporcion = min(
            1.0,
            max(0.0, aleatorio.gauss(ocupacion_media, 0.05))
        )

        mantenimiento = 0

        if capacidad > 1 and aleatorio.random() < 0.10:
            mantenimiento = aleatorio.randint(
                1,
                max(1, capacidad // 10)
            )

        ocupadas = round(
            (capacidad - mantenimiento) * proporcion
        )

        disponibles = capacidad - mantenimiento - ocupadas

        if id_registro in ids_anomalos:
            momento += desplazamiento

        yield {
            "id_registro_cama": id_registro,
            "sede_id": sede["id_sede"],
            "tip_unidad": tipo_unidad,
            "fec_hora_registro": momento.isoformat(sep=" "),
            "num_camas_ocupadas": ocupadas,
            "num_camas_disp": disponibles,
            "num_camas_mant": mantenimiento,
            "motivo_indisponibilidad": (
                "Mantenimiento programado"
                if mantenimiento > 0
                else None
            )
        }

    print(
        f"Fechas fuera del perioddo generadas: "
        f"{cantidad_anomalias}"
    )

# Construcction de archivos con datos generados. se modificó la forma de generar los registros ahora en lugar de la lista coompleta, genera un registro-> escribelo en json y csv -> continua
def guardar_archivos(tabla, registros, carpeta):
    registros = iter(registros)
    primero = next(registros, None)

    if primero is None:
        raise ValueError(f"No hay registros para {tabla}.")

    campos = list(primero.keys())

    with open(
        carpeta / f"{tabla}.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo_csv:

        with open (
            carpeta / f"{tabla}.json",
            "w",
            encoding="utf-8"
        ) as archivo_json:

            escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
            escritor.writeheader()
            escritor.writerow(primero)

            archivo_json.write("[\n")
            json.dump(primero, archivo_json, ensure_ascii=False)

            cantidad = 1

            for registro in registros:
                escritor.writerow(registro)

                archivo_json.write(",\n")
                json.dump(
                    registro,
                    archivo_json,
                    ensure_ascii=False
                )

                cantidad += 1

            archivo_json.write("\n]\n")

    
    print(f"{tabla}: {cantidad} registros, CSV y JSON")

# Exportacion de archivos egenrados.
guardar_archivos("cat_pais", paises, carpeta_salida)
guardar_archivos("cat_ciudad", ciudades, carpeta_salida)
guardar_archivos("red_sedes", sedes, carpeta_salida)
guardar_archivos("med_planta", medicos, carpeta_salida)
guardar_archivos("pac_registro", pacientes, carpeta_salida)
guardar_archivos("gcm_camas", generar_camas(), carpeta_salida)

print(f"\nArchivos guardados en: {carpeta_salida}")