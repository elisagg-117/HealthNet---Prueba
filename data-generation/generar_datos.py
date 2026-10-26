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

        proporcion = min(1.0,max(0.0, aleatorio.gauss(ocupacion_media, 0.05))        )

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

# Armado de informacion de encuentros o atenciones v2
def generar_encuentros(cantidad):
    # buscamos una sede
    sedes_por_id = {
        sede["id_sede"]: sede
        for sede in sedes
    }
    # relacionamos una ciudad con su pais
    pais_por_ciudad = {
        ciudad["id_ciudad"]: ciudad["pais_id"]
        for ciudad in ciudades
    }
    # generamos una lista de pacientes por pais
    pacientes_por_pais = {
        pais["id_pais"]: []
        for pais in paises
    }
    #agrupamos a los pacientes segun su residencia
    for paciente in pacientes:
        pais_id = pais_por_ciudad[paciente["ciudad_res_id"]]
        pacientes_por_pais[pais_id].append(paciente)

    # seleccion intencionada de medicos para la primera prueba de generacion
    medicos_elegibles = [
        medico
        for medico in medicos
        if medico["estado_activo"]
    ]

    if not medicos_elegibles:
        raise ValueError("No hay médicos activos.")

    diagnosticos_por_especialidad = {
        "Medicina general": ["J00", "J06.9"],
        "Medicina interna": ["I10", "E11.9"],
        "Pediatría": ["J00", "J06.9"],
        "Cardiología": ["I10"],
        "Ginecología": ["N76.0"],
        "Ortopedia": ["M54.9"]
    }

    inicio = datetime.fromisoformat(config["fecha_inicio"])
    fin = datetime.fromisoformat(config["fecha_fin"])
    dias_periodo = (fin - inicio).days


    procedimientos_por_especialidad = {
        "Medicina general": ["PR001"],
        "Medicina interna": ["PR001", "PR002"],
        "Pediatría": ["PR001"],
        "Cardiología": ["PR002"],
        "Ginecología": ["PR001"],
        "Ortopedia": ["PR003"]
    }

    precios_procedimientos = {
        "PR001": 20,
        "PR002": 35,
        "PR003": 40
    }

    factores_complejidad = {
        "Alta": 1.5,
        "Media": 1.2,
        "Baja": 1.0
    }

    for numero in range(1, cantidad + 1):
        medico = aleatorio.choice(medicos_elegibles)
        sede = sedes_por_id[medico["sede_id"]]
        especialidad = medico["esp_principal"]

        paciente = None

        fec_registro = inicio + timedelta(
            days=aleatorio.randint(0, dias_periodo),
            hours=aleatorio.randint(8, 17),
            minutes=aleatorio.randint(0, 59)
        )


        for intento in range(1000):
            candidato = aleatorio.choice(pacientes_por_pais[sede["pais_id"]])
            nacimiento = date.fromisoformat(candidato["fec_nac"])
            edad = fec_registro.year - nacimiento.year

            if (fec_registro.month, fec_registro.day) < (
                nacimiento.month,
                nacimiento.day
            ):
                edad -= 1

            if especialidad == "Pediatría" and edad >= 18:
                continue

            if edad < 18 and especialidad not in (
                "Medicina general",
                "Pediatría"
            ):
                continue

            if (
                especialidad == "Ginecología"
                and candidato["genero"] != "F"
            ):
                continue

            paciente = candidato
            break

        if paciente is None:
            raise ValueError(
                f"No se ha encontrado un paciente compatible "
                f"para {especialidad} en el pais "
                f"{sede['pais_id']}."
            )

        fec_inicio_atencion = fec_registro + timedelta(
            minutes=aleatorio.randint(15, 90)
        )

        fec_egreso = fec_inicio_atencion + timedelta(
            minutes=aleatorio.randint(15, 45)
        )

        tip_consulta = aleatorio.choice([
            "Primera vez",
            "Control"
        ])

        tarifa_base = 60 if tip_consulta == "Primera vez" else 45
        #buscamos el multiplicador de precio simulado  de acuerdo a la complejidad de la sede para construir una tarifa
        factor = factores_complejidad[sede["nivel_complejidad"]]

        diag_principal = aleatorio.choice(diagnosticos_por_especialidad[especialidad])

        diag_secundario = None

        if (edad >= 18 and aleatorio.random() < config["porcentaje_diag_secundario"]):
            opciones = [
                codigo
                for codigo in ["I10", "E11.9"]
                if codigo != diag_principal
            ]

            diag_secundario = aleatorio.choice(opciones)

        cod_procedimientos = None
        costo_procedimientos = 0

        if (aleatorio.random() < config["porcentaje_procedimientos"]):
            opciones = procedimientos_por_especialidad[especialidad]

            seleccionados = aleatorio.sample(opciones,aleatorio.randint(1, len(opciones)) )

            cod_procedimientos = ";".join(seleccionados)

            for codigo in seleccionados:
                costo_procedimientos += precios_procedimientos[codigo]       


        # incluimos una variacion simulada ahsta de 10% en vr factrurado al considerar el tipo de consulta y complejidad de sede evitando total aleatoriedad
        vr_facturado = round( (tarifa_base + costo_procedimientos) * factor * aleatorio.uniform(0.9, 1.1),2)

        yield {
            "id_encuentro": f"ENC-{numero:08d}",
            "pac_id": paciente["id_pac"],
            "med_id": medico["id_med"],
            "sede_id": sede["id_sede"],
            "fec_registro": fec_registro.isoformat(sep=" "),
            "fec_inicio_atencion": (
                fec_inicio_atencion.isoformat(sep=" ")
            ),
            "fec_egreso": fec_egreso.isoformat(sep=" "),
            "tip_consulta": tip_consulta,
            "esp_atendida": medico["esp_principal"],
            "diag_principal_cie10": diag_principal,
            "diag_sec1_cie10": diag_secundario,
            "cod_procedimientos": cod_procedimientos,
            "vr_facturado": vr_facturado,
            "estado_factura": "Facturada"
        }

# Armado de informacion de dispensacion
def generar_dispensaciones(cantidad):
    medicamentos = [
        {
            "codigo": "MED001",
            "nombre": "Medicamento A (caja)",
            "precio": 10.0
        },
        {
            "codigo": "MED002",
            "nombre": "Medicamento B (caja)",
            "precio": 20.0
        },
        {
            "codigo": "MED003",
            "nombre": "Medicamento C (caja)",
            "precio": 30.0
        }
    ]
    # ubicamos el archivo de encuentros creado anterioremente
    ruta_encuentros = (carpeta_salida / "hce_encuentros.csv")
    contador = 0
    #selecciona los num de registros a duplicar
    registros_a_duplicar = set(aleatorio.sample(range(1, cantidad + 1),round(cantidad * config["porcentaje_anomalias"])))

    with open(
        ruta_encuentros,
        newline="",
        encoding="utf-8"
    ) as archivo:

        lector = csv.DictReader(archivo)

        for encuentro in lector:
            numero_medicamentos = aleatorio.choices(
                [1, 2, 3],
                weights=[50, 35, 15],
                k=1
            )[0]

            seleccionados = aleatorio.sample(medicamentos,numero_medicamentos)

            for medicamento in seleccionados:
                if contador >= cantidad:
                    break

                contador += 1

                fec_dispensacion = (datetime.fromisoformat(encuentro["fec_egreso"])+ timedelta( minutes=aleatorio.randint(0, 90)))
                #definicion de nuestro diccionario
                registro = {
                    "id_dispensacion": f"DISP-{contador:08d}",
                    "encuentro_id": encuentro["id_encuentro"],
                    "pac_id": int(encuentro["pac_id"]),
                    "sede_id": int(encuentro["sede_id"]),
                    "fec_dispensacion": (
                        fec_dispensacion.isoformat(sep=" ")
                    ),
                    "cod_medicamento": medicamento["codigo"],
                    "nom_medicamento": medicamento["nombre"],
                    "cantidad": aleatorio.choices(
                        [1, 2, 3],
                        weights=[60, 30, 10],
                        k=1
                    )[0],
                    "vr_unitario": medicamento["precio"],
                    "tip_prescripcion": "Ambulatoria"
                }
                # entrega del registro de dispensacion original para utilizar sus datos
                yield registro
                # cambiamos el identificador, lo demas permanece igual
                if contador in registros_a_duplicar:
                    duplicado = registro.copy()
                    duplicado["id_dispensacion"] = (f"DISP-DUP-{contador:08d}")
                    #entrgamos la copia del registro apra que se escriba tambien
                    yield duplicado

            if contador >= cantidad:
                break

    if contador < cantidad:
        raise ValueError(
            f"Se generaron {contador} dispensaciones; "
            f"se solicitaron {cantidad}."
        )



# Construcction de archivos con datos generados. se modificó la forma de generar los registros ahora en lugar de la lista coompleta, genera un registro-> escribe en json y csv -> continua
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
guardar_archivos("hce_encuentros", generar_encuentros(config["cantidad_encuentros"]),carpeta_salida)
guardar_archivos("far_dispensacion", generar_dispensaciones(config["cantidad_dispensaciones"]),carpeta_salida)


print(f"\nArchivos guardados en: {carpeta_salida}")