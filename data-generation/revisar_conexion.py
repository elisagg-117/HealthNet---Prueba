from getpass import getpass

#modulo pyscopg3
import psycopg

db_name = input("Nombre de la base de datos: ").strip()
username = input("usuario de postgresql:  ").strip()

with psycopg.connect(
	host="127.0.0.1",
	port=5431,
	dbname=db_name,
	user=username,
	password=getpass("Contraseña de postgresql: "),
	connect_timeout=5

) as conexion:
	
	# ejecutamos la consulta, recuperamos la fila de ese resultado y lo guardamos en la variable datos conectividad
	datos_conexion = conexion.execute(
		"""
		select
			current_database(),
			current_user,
			current_setting('server_version');
		"""
	).fetchone()

	print(f"\nBase de datos: {datos_conexion[0]}")
	print(f"\nUsuario conectado: {datos_conexion[1]}")
	print(f"\nVersion de motor postgreslq: {datos_conexion[2]}")

	tablas = conexion.execute (
		""" select table_name from information_schema.tables where table_schema = 'operacional' and table_type = 'BASE TABLE' order by table_name; """
	).fetchall()

	print(f"\nTablas encontradas: {len(tablas)}")

	for tabla in tablas:
		print(f" - {tabla[0]}")