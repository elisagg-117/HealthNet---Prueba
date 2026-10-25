from getpass import getpass

from pathlib import Path
#modulo psycopg 3
import psycopg


carpeta_base = Path(__file__).resolve().parent

#rutas de archivos 
ruta_paises = carpeta_base / "output" / "cat_pais.csv"
ruta_ciudades = carpeta_base / "output" / "cat_ciudad.csv"
ruta_sedes = carpeta_base / "output" / "red_sedes.csv"

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

print("\nProceso finalizado: ")
print(f"Paises: {cantidad_cargada}")
print(f"Ciudades: {cantidad_ciudades}")
print(f"Sedes: {cantidad_sedes}")