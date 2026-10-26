# Infraestructura HealthNet

Usamos Bicep para crear los recursos de Azure y guardar su configuración en Git. Como Azure administra el estado, por lo que no necesitamos un backend de Terraform

## Estado actual

Los recursos de DEV ya están desplegados. También validamos la plantilla con los parámetros de PROD, pero todavía no desplegamos su infraestructura completa.

## Archivos codigo IaC

- `main.bicep`: crea el grupo de recursos y llama al módulo
- `resources.bicep`: define los recursos y permisos
- `parameters/dev.parameters.json`: configuración de desarrollo
- `parameters/prd.parameters.json`: configuración de producción

## Recursos desplegados en DEV

Grupo de recursos
    nombre: rg-healthnet-dev 
    region:southcentralus 
    proposito: Agrupar los recursos
Storage ADLS Gen2
    nombre: sthealthnetdev2026eg
    region: southcentralus
    proposito: Guardar los datos
Contenedores
    nombres: bronze, silver y gold
    region: La del Storage
    proposito: Separar las capas
Data Factory
    nombre: adf-healthnet-dev-2026eg
    region: southcentralus
    proposito: Ejecutar los procesos de datos
Self-hosted Integration Runtime 
    nombre: ir-healthnet-local-dev
    region: Asociado a ADF
    proposito: conectar con PostgreSQL local
Key Vault 
    nombre: kv-healthnet-dev-2026eg
    region: southcentralus
    proposito: Guardar las credenciales que usaremos
Log Analytics 
    nombre: law-healthnet-dev
    region: southcentralus
    proposito: Consultar los registros de ejecución
Configuración de diagnóstico 
    nombre: diag-adf-law
    region: Asociada a ADF
    propsito:Enviar registros a Log Analytics
Action Group 
    nombre: ag-healthnet-dev
    region: global
    proposito: Enviar notificaciones por correo

Data Factory tiene identidad administrada y estos permisos:

- `Storage Blob Data Contributor` en el Storage
- `Key Vault Secrets User` en el Key Vault

## Parámetros

Los archivos JSON permiten cambiar: (Configuracion --- Parametros)

Ambiente y ubicación: resourceGroupName, location, environment
Almacenamiento: storageAccountName, storageSku, containerNames
Data Factory: dataFactoryName, selfHostedIrName
Key Vault: keyVaultName, keyVaultSku
Monitoreo: logAnalyticsName, logRetentionDays, factoryDiagnosticsName
Notificaciones: actionGroupName, actionGroupLocation, alertEmail
Gestión de secretos: vaultOperatorObjectId

No se guardan contraseñas ni claves en estos archivos. Antes de desplegar en otra suscripción, revisar los nombres, la región, el correo y vaultOperatorObjectId. Este último debe ser el Object ID del usuario que administrará los secretos en el directorio de destino.

## Requisitos

- Azure CLI y Bicep instalados
- Sesión iniciada en la suscripción correcta
- Permisos para crear recursos y asignar roles

Los proveedores utilizados son `Microsoft.Storage`, `Microsoft.DataFactory`, `Microsoft.KeyVault`, `Microsoft.OperationalInsights` y `Microsoft.Insights`

Si alguno no está registrado, registrarlo antes de desplegar. Durante la prueba fue necesario registrar Storage y Key Vault.

## Validar y desplegar

Ejecutar desde la raíz del repositorio. Reemplazar `ID..` por el ID de la suscripcion:
# Powershell
$subscriptionId = "ID"
$ambiente = "dev"


Validar:
# Powershell
az deployment sub validate --subscription $subscriptionId --name "healthnet-$ambiente" --location southcentralus --template-file .\infra\main.bicep --parameters "@infra/parameters/$ambiente.parameters.json"


Revisar los cambios:
# Powershell
az deployment sub what-if --subscription $subscriptionId --name "healthnet-$ambiente" --location southcentralus --template-file .\infra\main.bicep --parameters "@infra/parameters/$ambiente.parameters.json"


Después de revisar el resultado, desplegar:
# Powershell
az deployment sub create --subscription $subscriptionId --name "healthnet-$ambiente" --location southcentralus --template-file .\infra\main.bicep --parameters "@infra/parameters/$ambiente.parameters.json"

Para usar PROD, cambiar `$ambiente` a `"prd"`

## Acceso y monitoreo

Storage exige HTTPS, no permite acceso anónimo o autenticación con claves de cuenta. Se utiliza Microsoft Entra ID. Los recursos usan endpoints públicos; no se han creado private Endpoints.

ADF envía los registros de pipelines, actividades y triggers a Log Analytics. El workspace tiene una retrencion configurada de 30 días.

Las salidas de Bicep incluyen nombres, identificadores y endpoints de los recursos, sin claves ni contraseñas.

# Preparación después del despliegue

Bicep crea la infraestructura. Para conectar el origen y ejecutar las cargas también se necesita:
- Ejecutar data-generation/sql/03_permisos_lectura_adf.sql en la base de origen para crear adf_lectura y asignarle una contraseña desde PostgreSQL
- En ADF, entrar a Manage --> Integration runtimes, seleccionar el Self-hosted IR y descargar su agente. Instalarlo en el equipo con acceso a PostgreSQL y registrarlo con la clave proporcionada por ADF
- Instalar OpenJDK 11 ,configurar la variable de sistema JAVA_HOME con la carpeta de instalación y reiniciar el servicio del agente. Se utiliza para generar Parquet durante la copia.
- Crear en Key Vault el secreto postgres-adf-password con la contraseña de adf_lectura.
- Configurar en ADF las conexiones, datasets, Data Flow y pipelines tomando como referencia los JSON de /pipelines. Probar las conexiones y publicar los cambios
- Los JSON guardan la configuración utilizada; este proyecto no incluye un script que restaure automáticamente todos los objetos de ADF
- El Action Group está creado. Las reglas de alerta quedan pendientes.

# Ejecución en Azure
En Data Factory:
1. Ejecutar `pl_bronze_operacional` con las nueve tablas configuradas y esperar a que termine correctamente
2. Identificar la carpeta generada para `gcm_camas`. Su ruta tiene esta estructura: operacional/gcm_camas/AAAA/MM/DD/batch_id=ID_DE_EJECUCION_BRONZE

3. Ejecutar `pl_silver_camas`, indicando esa ruta en el parámetro `p_carpeta_bronze`

4. Revisar en Monitor el estado de las actividades y los registros escritos en ambos sinks

Silver separa los registros conformes y rechazados. No se configuró la limpieza de las carpetas de destino, por lo que repetir Silver sobre el mismo lote puede duplicar los datos almacenados

## Configuración comprobada

- Agente del Self-hosted Integration Runtime instalado y en linea
- Contraseña de adf_lectura guardada en Key Vault
- Conexiones de ADF a Key Vault, PostgreSQL y Data Lake probadas correctamente
- Revision de Log Analytics W los registros de las ejecuciones

Las capturas de evidencia se guardan en `/docs/FASE-2`