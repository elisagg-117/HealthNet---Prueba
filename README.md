\------------------------------------------------------------------------------

\-- DESCRIPCION COMPLETA DE LA SOLUCION

\------------------------------------------------------------------------------
Escenario C: Salud. Plataforma: Microsoft Azure
Origen: PostgreSQL local en Docker

El escenario relaciona pacientes, atención médica, sedes, camas,dispensaciones y citas. Me interesó porque procesar esta información puede ayudar a tomar decisiones y encontrar patrones sobre la atención y el uso de los recursos, en un sector tan importante como la salud pública.

Elegí Azure porque es la plataforma con la que tengo más experiencia. Para este ejercicio utilicé Data Factory para mover y transformar los datos, Data Lake Storage para las capas Bronze y Silver, y Key Vault para guardar la contraseña de conexión. Esto me permitió trabajar con servicios integrados y enfocarme en construir y tratar de comprobar el flujo de datos.


# Información general - Base de datos:
* Estructura creada: esquema operacional, 7 tablas del escenario y dos catálogos auxiliares
--> Se considero crear un esquema personalizado y no usar el público (default) como buena práctica para organización
Las capturas de evidencia se guardan en `/docs/FASE-1`


# Informacion para generacion y carga de datos
Se necesita Python y PostgreSQL en ejecución. La conexión local utiliza 127.0.0.1 y el puerto 5431
Crear la base de datos y ejecutar en ella el archivo: data-generation/sql/01_create_source_tables.sql
Este script crea las 9 tablas utilizadas como origen de datos:

cat_pais -> Catálogo de países	- 3 registros
cat_ciudad -> Catálogo de ciudades - 9 registros
red_sedes -> Catálogo de sedes de la red - 82 registros
med_planta -> Médicos registrados - 2000 registros
pac_registro -> Pacientes registrados - 100000 registros
gcm_camas -> Información de camas - 500000 registros
hce_encuentros -> Encuentros clínicos - 2000000 registros
far_dispensacion -> Dispensaciones de medicamentos - 3030000 registros
age_citas -> Citas médicas - 1500000 registros

El volumen total esperado es de 7132094 registros.

Las tablas cat_pais, cat_ciudad y red_sedes funcionan como tablas auxiliares para mantener consistencia en las relaciones del resto del modelo.

## Preparación del entorno

Desde la raíz del proyecto, preparar el entorno de Python:
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install "psycopg[binary]"

Revisar data-generation/config.json, donde se definen la semilla y las cantidades de datos


## Generar los archivos CSV y JSON:
.\.venv\Scripts\python.exe .\data-generation\generar_datos.py

Los archivos se guardan en data-generation/output/

## Anomalías controladas

Durante la generación se incluyen de forma intencional algunos casos utilizados posteriormente para validar reglas de calidad de datos.
- gcm_camas: 5000 registros con fechas fuera del período esperado
- far_dispensacion: 30000 duplicados, incluidos dentro de los 3030000 registros generados
- age_citas: 12068 registros con tiempos de espera negativos

También se generan valores nulos de forma controlada para representar situaciones válidas del dominio.
En age_citas, 75,000 registros, equivalentes al 5 % del total, contienen esp_solicitada como valor nulo.

## Cargar los datos en PostgreSQL:
.\.venv\Scripts\python.exe .\data-generation\cargar_datos.py

El cargador solicita el nombre de la base, usuario y contraseña. Conserva las tablas que ya contienen registros

## Validación de la carga
Para comprobar las cantidades cargadas en cada tabla, ejecutar:
data-generation/sql/02_validar_carga.sql
El archivo: docs/evidencia_carga.csv se conserva como resultado de esta validación ejecutada en la bd y presenta como evidencia
 

## Herramientas utilizadas
PostgreSQL
Propósito: Almacenar los datos de origen en tablas relacionadas

Docker
Propósito: Ejecutar PostgreSQL y pgAdmin en el entorno local

Python
Propósito: Generar los datos de prueba y cargarlos en PostgreSQL

Azure Data Factory
Propósito: Ejecutar y controlar las cargas de datos

ADLS Gen2
Propósito: Almacenar los datos de las capas Bronze, Silver y Gold

Parquet
Propósito: Guardar los datos de Bronze en el formato solicitado

Bicep
Propósito: Definir y desplegar los recursos de Azure mediante código

Key Vault
Propósito: Guardar la contraseña de conexión utilizada por ADF

Log Analytics
Propósito: Centralizar los registros de ejecución de ADF

Action Group
Propósito: Definir el destinatario de las futuras notificaciones de alerta


## Resultado de Bronze

Se comprobaron 7,132,094 registros leídos y escritos en 9 archivos.
Cada registro incluye fecha_ingesta, sistema_origen e id_lote.
Las carpetas se organizan por tabla, año, mes, día y lote.
Las capturas de evidencia se guardan en `/docs/FASE-3`
\
## Resultado de Silver
Se procesó la tabla gcm_camas desde Bronze para separar los registros según su fecha.
El periodo válido es del 1 de octubre de 2025 al 30 de septiembre de 2026.
Registros procesados: 500000.
Conformes: 495000.
Rechazados por fechas fuera del período: 5000.
Ambos resultados se guardaron en Parquet dentro de Silver, en carpetas separadas. Los rechazados incluyen la columna motivo_error.
La ejecución terminó correctamente. Las capturas están en /docs y los JSON de configuración en /pipelines.
Este avance de Silver cubre únicamente la validación de fechas de camas.
Las capturas de evidencia se guardan en `/docs/FASE-3`

La preparación y ejecución en Azure se describe en [infra/README.md](infra/README.md)
