# Pipeline ETL con AWS Glue y S3 - Guía Visual

## 📋 Descripción

Este proyecto implementa un pipeline ETL (Extract, Transform, Load) usando AWS Glue y S3 para procesar datos de ventas, inventario y clientes a través de la consola web de AWS.

**¿Qué hace el ETL?**
- 📥 **Extract**: Lee archivos CSV desde S3 (facturas, inventario, usuarios)
- 🔄 **Transform**: Procesa y analiza los datos (ventas por cliente, productos más vendidos, etc.)
- 📤 **Load**: Guarda los resultados procesados en S3

## 🏗️ Arquitectura

```
S3 Bronze (datos raw)  →  AWS Glue Job  →  S3 Silver (datos procesados)
     ↓                        ↓                    ↓
  tickets.csv            Transformaciones      ventas_por_cliente.csv
  items.csv                   ETL             productos_vendidos.csv
  clients.csv                                 ventas_por_dia.csv
```

## 🚀 Guía de Implementación (Consola AWS)

### Paso 1: Crear Bucket S3

1. **Ir a la consola de S3**
   - Buscar "S3" en la consola de AWS
   - Hacer clic en "Create bucket"

2. **Configurar el bucket**
   - **Bucket name**: `datalake-utn`
   - **Region**: Seleccionar tu región preferida (ej: us-east-1)
   - Dejar las demás opciones por defecto
   - Hacer clic en "Create bucket"

3. **Crear carpetas**
   - Entrar al bucket `datalake-utn`
   - Hacer clic en "Create folder"
   - Crear carpeta llamada `bronze`
   - Hacer clic en "Create folder" nuevamente
   - Crear carpeta llamada `silver`

### Paso 2: Crear Rol IAM para Glue

1. **Ir a la consola de IAM**
   - Buscar "IAM" en la consola de AWS
   - En el menú izquierdo, hacer clic en "Roles"

2. **Crear nuevo rol**
   - Hacer clic en "Create role"
   - **Trusted entity type**: AWS service
   - **Service or use case**: Glue
   - Hacer clic en "Next"

3. **Adjuntar políticas**
   - Buscar y seleccionar: `AWSGlueServiceRole`
   - Buscar y seleccionar: `AmazonS3FullAccess`
   - Hacer clic en "Next"

4. **Configurar rol**
   - **Role name**: `GlueETLRole`
   - **Description**: `Rol para jobs de Glue ETL`
   - Hacer clic en "Create role"

### Paso 3: Preparar Archivos CSV

#### Crear archivos de ejemplo en tu computadora:

**tickets.csv**
```csv
ID_Cliente,Fecha,ID_Articulo,Cantidad,Total
1,2024-01-15,101,2,150.00
2,2024-01-16,102,1,75.50
3,2024-01-17,101,3,225.00
1,2024-01-18,103,1,89.99
2,2024-01-19,102,2,151.00
```

**items.csv**
```csv
ID_Articulo,Nombre_Articulo,Stock,Precio,Fecha_Ultima_Reposicion
101,Laptop HP,10,750.00,2024-01-10
102,Mouse Inalámbrico,25,75.50,2024-01-12
103,Teclado Mecánico,15,89.99,2024-01-14
```

**clients.csv**
```csv
ID_Cliente,Nombre,Apellido,Tipo_Cliente,Fecha_Registro
1,Juan,Pérez,Premium,2023-06-15
2,María,González,Regular,2023-08-20
3,Carlos,López,Premium,2023-09-10
```

### Paso 4: Subir Archivos a S3

1. **Ir al bucket S3**
   - Volver a la consola de S3
   - Hacer clic en el bucket `datalake-utn`
   - Entrar a la carpeta `bronze`

2. **Subir archivos**
   - Hacer clic en "Upload"
   - Arrastar los 3 archivos CSV o hacer clic en "Add files"
   - Seleccionar: `tickets.csv`, `items.csv`, `clients.csv`
   - Hacer clic en "Upload"

3. **Verificar**
   - Confirmar que los 3 archivos aparezcan en `s3://datalake-utn/bronze/`

### Paso 5: Subir Script del Job Glue

Script Python Shell

2. **Subir script a S3**
   - Ir a S3 y buscar el bucket que empiece con `aws-glue-assets-`
   - Si no existe, crear bucket llamado `aws-glue-scripts-tu-nombre`
   - Crear carpeta `scripts` dentro del bucket
   - Subir el archivo `etl-script.py` a esa carpeta

### Paso 6: Crear Job de Glue

1. **Ir a la consola de AWS Glue**
   - Buscar "Glue" en la consola de AWS
   - En el menú izquierdo, hacer clic en "Jobs"

2. **Crear nuevo job**
   - Hacer clic en "Create job"
   - **Job name**: `etl-pipeline-utn`
   - **IAM Role**: Seleccionar `GlueETLRole`
   - **Type**: Python shell script
   - **Glue version**: 3.0
   - **Python version**: 3.9

3. **Configurar script**
   - **Script path**: Buscar el archivo `etl-script.py` que subiste a S3
   - **Allocated capacity**: 0.0625 DPU
   - Hacer clic en "Create job"

### Paso 7: Ejecutar el Job

1. **En la página del job**
   - Hacer clic en "Run job"
   - Esperar a que el estado cambie a "Running"
   - El job debería completarse en 1-2 minutos

2. **Monitorear ejecución**
   - En la pestaña "Runs", ver el progreso
   - Si el estado es "Succeeded", ¡todo salió bien!
   - Si es "Failed", hacer clic en "Logs" para ver el error

### Paso 8: Verificar Resultados

1. **Ir a S3**
   - Navegar a `s3://datalake-utn/silver/`
   - Deberías ver 3 archivos nuevos:
     - `ventas_por_cliente.csv`
     - `productos_mas_vendidos.csv`
     - `ventas_por_dia.csv`

2. **Descargar y revisar**
   - Hacer clic en cada archivo
   - Hacer clic en "Download" para verlos en Excel/Google Sheets

## 📊 Resultados Esperados

**ventas_por_cliente.csv**
```csv
ID_Cliente,Total,Nombre,Apellido
1,239.99,Juan,Pérez
2,226.50,María,González
3,225.00,Carlos,López
```

**productos_mas_vendidos.csv**
```csv
ID_Articulo,Cantidad,Nombre_Articulo
101,5,Laptop HP
102,3,Mouse Inalámbrico
103,1,Teclado Mecánico
```

**ventas_por_dia.csv**
```csv
Fecha,Total
2024-01-15,150.00
2024-01-16,75.50
2024-01-17,225.00
2024-01-18,89.99
2024-01-19,151.00
```

## 🔧 Monitoreo y Debugging

### Ver logs del job
1. **En AWS Glue**
   - Ir a "Jobs" → Seleccionar tu job
   - Hacer clic en la pestaña "Runs"
   - Hacer clic en "Logs" de la ejecución

2. **En CloudWatch**
   - Buscar "CloudWatch" en AWS
   - Ir a "Log groups"
   - Buscar `/aws-glue/python-jobs/etl-pipeline-utn`

### Solución de problemas comunes

#### ❌ "Access Denied"
**Causa**: Permisos insuficientes
**Solución**: 
- Verificar que el rol `GlueETLRole` tenga las políticas correctas
- Ir a IAM → Roles → GlueETLRole → Verificar políticas adjuntas

#### ❌ "No such file or directory" 
**Causa**: Archivos no encontrados
**Solución**:
- Verificar que los archivos CSV estén en `s3://datalake-utn/bronze/`
- Verificar nombres exactos: `tickets.csv`, `items.csv`, `clients.csv`

#### ❌ Job falla en transformación
**Causa**: Estructura de datos incorrecta
**Solución**:
- Verificar que los CSV tengan las columnas correctas
- Revisar logs para ver el error específico

## 🎯 Próximos Pasos

1. **Automatización**
   - Crear trigger para ejecutar el job automáticamente
   - Configurar notificaciones por email

2. **Expansión**
   - Agregar más fuentes de datos
   - Crear visualizaciones con QuickSight

3. **Monitoreo**
   - Configurar alarmas en CloudWatch
   - Crear dashboard de métricas

## 💡 Tips

- **Costo**: Un job pequeño cuesta ~$0.01-0.05 por ejecución
- **Tiempo**: Jobs simples tardan 1-3 minutos
- **Testing**: Siempre probar con datos pequeños primero
- **Backup**: Mantener copias de los scripts importantes

---

**¡Tu pipeline ETL está funcionando!** 🎉

Para cualquier duda, revisar los logs en CloudWatch o contactar al equipo de soporte.