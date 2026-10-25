from getpass import getpass

from pathlib import Path
#modulo pyscopg3
import psycopg


carpeta_base = Path(__file__).resolve().parent
ruta_csv = carpeta_base / "output" / "cat_ciudad.csv"

db_name = input("Nombre de la base de datos: ").strip()
username = input("usuario de postgresql:  ").strip()
with psycopg.connect(
    host="127.0.0.1",
    port=5431,
    dbname=db_name,
    user=username,
    password=getpass("Contraseña de PostgreSQL: "),
    connect_timeout=5,
) as conexion:

    with conexion.cursor() as cursor:

        cursor.execute("select count(*) from operacional.cat_ciudad;")
        
        with open(ruta_csv, "rb") as archivo:
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

        cursor.execute("select count(*) from operacional.cat_ciudad;")
        cantidad_ciudades = cursor.fetchone()[0]

print("\nCarga realizada")
print(f"Ciudades: {cantidad_ciudades}")