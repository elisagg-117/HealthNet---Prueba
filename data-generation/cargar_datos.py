from getpass import getpass

from pathlib import Path
#modulo psycopg 3
import psycopg


carpeta_base = Path(__file__).resolve().parent

#rutas de archivos 
ruta_paises = carpeta_base / "output" / "cat_pais.csv"
ruta_ciudades = carpeta_base / "output" / "cat_ciudad.csv"
ruta_sedes = carpeta_base / "output" / "red_sedes.csv"
ruta_medicos = carpeta_base / "output" / "med_planta.csv"
ruta_pacientes = carpeta_base / "output" / "pac_registro.csv"
ruta_camas = carpeta_base / "output" / "gcm_camas.csv"
ruta_encuentros = carpeta_base / "output" / "hce_encuentros.csv"
ruta_dispensaciones = carpeta_base / "output" / "far_dispensacion.csv"

#info para conectar a la bd
db_name = input("Nombre de la base de datos: ").strip()
username = input("Nombre del usuario ").strip()

with psycopg.connect(
    host="127.0.0.1",
    port=5431,
    dbname=db_name,
    user=username,
    password=getpass("Contraseña de PostgreSQL: "),
    connect_timeout=5,
) as conexion:

    with conexion.cursor() as cursor:

        #cargamos paises sol;o si no hay ya cargados
        cursor.execute("select count(*) from operacional.cat_pais;")
        cantidad_actual = cursor.fetchone()[0]

        if cantidad_actual == 0:
            with open(ruta_paises, "rb") as archivo:
                with cursor.copy(
                    """
                    COPY operacional.cat_pais (id_pais, nom_pais)
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
                    """
                ) as copia:

                    bloque = archivo.read(1024 * 1024)

                    while bloque:
                        copia.write(bloque)
                        bloque = archivo.read(1024 * 1024)

            cursor.execute(
                """
                select setval(
                    pg_get_serial_sequence(
                        'operacional.cat_pais', 'id_pais'
                    ),
                    (select max(id_pais) from operacional.cat_pais)
                );
                """
            )
        else:
            print(
                f"cat_pais: se conservan "
                f"{cantidad_actual} registros existentes."
            )

        cursor.execute("select count(*) from operacional.cat_pais;")
        cantidad_cargada = cursor.fetchone()[0]

         #cargamos ciudades sol;o si no hay ya cargados
        cursor.execute("select count(*) from operacional.cat_ciudad;")
        cantidad_actual = cursor.fetchone()[0]

        if cantidad_actual == 0:
            with open(ruta_ciudades, "rb") as archivo:
                with cursor.copy(
                    """
                    COPY operacional.cat_ciudad (
                        id_ciudad, nom_ciudad, pais_id
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
                    """
                ) as copia:

                    bloque = archivo.read(1024 * 1024)

                    while bloque:
                        copia.write(bloque)
                        bloque = archivo.read(1024 * 1024)

            cursor.execute(
                """
                select setval(
                    pg_get_serial_sequence(
                        'operacional.cat_ciudad', 'id_ciudad'
                    ),
                    (select max(id_ciudad) from operacional.cat_ciudad)
                );
                """
            )
        else:
            print(
                f"cat_ciudad: se conservan "
                f"{cantidad_actual} registros existentes"
            )

        cursor.execute("select count(*) from operacional.cat_ciudad;")
        cantidad_ciudades = cursor.fetchone()[0]


        # cargar info de sedes
        cursor.execute("select count(*) from operacional.red_sedes;")
        cantidad_actual = cursor.fetchone()[0]

        if cantidad_actual == 0:
            with open(ruta_sedes, "rb") as archivo:
                with cursor.copy(
                    """
                    COPY operacional.red_sedes (
                        id_sede,
                        nom_sede,
                        tip_sede,
                        ciudad_id,
                        pais_id,
                        cap_camas_gen,
                        cap_camas_uci,
                        cap_camas_cirugia,
                        cap_camas_urg,
                        nivel_complejidad
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
                    """
                ) as copia:

                    bloque = archivo.read(1024 * 1024)

                    while bloque:
                        copia.write(bloque)
                        bloque = archivo.read(1024 * 1024)

            cursor.execute(
                """
                select setval(
                    pg_get_serial_sequence(
                        'operacional.red_sedes', 'id_sede'
                    ),
                    (select max(id_sede) from operacional.red_sedes)
                );
                """
            )
        else:
            print(
                f"red_sedes: se conservan "
                f"{cantidad_actual} registros existentes."
            )

        cursor.execute("select count(*) from operacional.red_sedes;")
        cantidad_sedes = cursor.fetchone()[0]

        # cargar info de medicos
        
        cursor.execute("select count(*) from operacional.med_planta;")
        cantidad_actual = cursor.fetchone()[0]

        if cantidad_actual == 0:
            with open(ruta_medicos, "rb") as archivo:
                with cursor.copy(
                    """
                    COPY operacional.med_planta (
                        id_med,
                        esp_principal,
                        esp_secundaria,
                        sede_id,
                        fec_ingreso,
                        tip_contrato,
                        jornada,
                        estado_activo
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
                    """
                ) as copia:

                    bloque = archivo.read(1024 * 1024)

                    while bloque:
                        copia.write(bloque)
                        bloque = archivo.read(1024 * 1024)

            cursor.execute(
                """
                select setval(
                    pg_get_serial_sequence(
                        'operacional.med_planta', 'id_med'
                    ),
                    (select max(id_med) from operacional.med_planta)
                );
                """
            )
        else:
            print(
                f"med_planta: se conservan "
                f"{cantidad_actual} registros existentes."
            )

        cursor.execute("select count(*) from operacional.med_planta;")
        cantidad_medicos = cursor.fetchone()[0]

        # cargar info de pacientes
        cursor.execute("select count(*) from operacional.pac_registro;")
        cantidad_actual = cursor.fetchone()[0]

        if cantidad_actual == 0:
            with open(ruta_pacientes, "rb") as archivo:
                with cursor.copy(
                    """
                    COPY operacional.pac_registro (
                        id_pac,
                        tip_doc,
                        num_doc_hash,
                        fec_nac,
                        genero,
                        ciudad_res_id,
                        tip_aseguradora,
                        id_eps,
                        estrato_socioec,
                        fec_primer_atencion,
                        activo
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
                    """
                ) as copia:
                    bloque = archivo.read(1024 * 1024)
                    while bloque:
                        copia.write(bloque)
                        bloque = archivo.read(1024 * 1024)

            cursor.execute(
                """
                select setval(
                    pg_get_serial_sequence(
                        'operacional.pac_registro', 'id_pac'
                    ),
                    (select max(id_pac) from operacional.pac_registro)
                );
                """
            )
        else:
            print(
                f"pac_registro: se conservan "
                f"{cantidad_actual} registros existentes."
            )

        cursor.execute("select count(*) from operacional.pac_registro;")
        cantidad_pacientes = cursor.fetchone()[0]

        # cargar info de camas ocupacion
        cursor.execute("select count(*) from operacional.gcm_camas;")
        cantidad_actual = cursor.fetchone()[0]

        if cantidad_actual == 0:
            with open(ruta_camas, "rb") as archivo:
                with cursor.copy(
                    """
                    COPY operacional.gcm_camas (
                        id_registro_cama,
                        sede_id,
                        tip_unidad,
                        fec_hora_registro,
                        num_camas_ocupadas,
                        num_camas_disp,
                        num_camas_mant,
                        motivo_indisponibilidad
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
                    """
                ) as copia:

                    bloque = archivo.read(1024 * 1024)

                    while bloque:
                        copia.write(bloque)
                        bloque = archivo.read(1024 * 1024)

            cursor.execute(
                """
                select setval(
                    pg_get_serial_sequence(
                        'operacional.gcm_camas',
                        'id_registro_cama'
                    ),
                    (
                        select max(id_registro_cama)
                        from operacional.gcm_camas
                    )
                );
                """
            )
        else:
            print(
                f"gcm_camas: se conservan "
                f"{cantidad_actual} registros existentes."
            )

        cursor.execute("select count(*) from operacional.gcm_camas;")
        cantidad_camas = cursor.fetchone()[0]

        # Cargar info de encuentros
        cursor.execute("select count(*) from operacional.hce_encuentros;")
        cantidad_actual = cursor.fetchone()[0]

        if cantidad_actual == 0:
            with open(ruta_encuentros, "rb") as archivo:
                with cursor.copy(
                    """
                    COPY operacional.hce_encuentros (
                        id_encuentro,
                        pac_id,
                        med_id,
                        sede_id,
                        fec_registro,
                        fec_inicio_atencion,
                        fec_egreso,
                        tip_consulta,
                        esp_atendida,
                        diag_principal_cie10,
                        diag_sec1_cie10,
                        cod_procedimientos,
                        vr_facturado,
                        estado_factura
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
                    """
                ) as copia:

                    bloque = archivo.read(1024 * 1024)

                    while bloque:
                        copia.write(bloque)
                        bloque = archivo.read(1024 * 1024)
        else:
            print(
                f"hce_encuentros: se conservan "
                f"{cantidad_actual} registros existentes."
            )

        cursor.execute("select count(*) from operacional.hce_encuentros;")
        cantidad_encuentros = cursor.fetchone()[0]

        # carga de informacion de dispensaciones con anomalias controladas
        cursor.execute("select count(*) from operacional.far_dispensacion;")
        cantidad_actual = cursor.fetchone()[0]

        if cantidad_actual == 0:
            with open(ruta_dispensaciones, "rb") as archivo:
                with cursor.copy(
                    """
                    COPY operacional.far_dispensacion (
                        id_dispensacion,
                        encuentro_id,
                        pac_id,
                        sede_id,
                        fec_dispensacion,
                        cod_medicamento,
                        nom_medicamento,
                        cantidad,
                        vr_unitario,
                        tip_prescripcion
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
                    """
                ) as copia:

                    bloque = archivo.read(1024 * 1024)

                    while bloque:
                        copia.write(bloque)
                        bloque = archivo.read(1024 * 1024)
        else:
            print(
                f"far_dispensacion: se conservan "
                f"{cantidad_actual} registros existentes."
            )

        cursor.execute(
            "select count(*) from operacional.far_dispensacion;"
        )
        cantidad_dispensaciones = cursor.fetchone()[0]


print("\nProceso finalizado: ")
print(f"Paises: {cantidad_cargada}")
print(f"Ciudades: {cantidad_ciudades}")
print(f"Sedes: {cantidad_sedes}")
print(f"Medicos: {cantidad_medicos}")
print(f"Pacientes: {cantidad_pacientes}")
print(f"Mediciones de camas: {cantidad_camas}")
print(f"Encuentros: {cantidad_encuentros}")
print(f"Dispensaciones: {cantidad_dispensaciones}")
