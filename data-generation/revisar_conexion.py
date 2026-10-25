from getpass import getpass

#modulo pyscopg3
import psycopg

db_name = input("Nombre de la base de datos: ").strip()
username = input("usuario de postgresql:  ").strip()

with .connect(
	host="127.0.0.1",
	port=5431,
	dbname=db_name,
	user=username,
	password=getpass("Contraseña de postgresql: "),
	connection_timeout=5

) as conexion:
	
# ejecutamos la consulta, recuperamos la fila de ese resultado y lo guardamos en la variable datos conectividad
datos_conectividad = conexion.execute(
	"""
	select
		current_database(),
		current_user,
		current_setting('server_version');
	"""
).fetchone()

