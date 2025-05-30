import pandas as pd
import boto3
from io import StringIO

# Configuración de AWS
s3 = boto3.client('s3')
bucket_name = 'datalake-utn'
input_prefix = 'bronze/'
output_prefix = 'silver/'

def read_csv_from_s3(file_name):
    response = s3.get_object(Bucket=bucket_name, Key=input_prefix + file_name)
    return pd.read_csv(StringIO(response['Body'].read().decode('utf-8')))

def write_csv_to_s3(df, file_name):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=bucket_name, Key=output_prefix + file_name, Body=csv_buffer.getvalue())

# Paso 1: Extracción (Extract)
# Leemos los tres CSV desde S3
df_facturas = read_csv_from_s3('tickets.csv')
df_inventario = read_csv_from_s3('items.csv')
df_usuarios = read_csv_from_s3('clients.csv')

# Mostramos las primeras filas de cada DataFrame
print("Facturas:")
print(df_facturas.head())
print("\nInventario:")
print(df_inventario.head())
print("\nUsuarios:")
print(df_usuarios.head())

# Paso 2: Transformación (Transform)

# 2.1 Convertimos las fechas a tipo datetime
df_facturas['Fecha'] = pd.to_datetime(df_facturas['Fecha'])
df_inventario['Fecha_Ultima_Reposicion'] = pd.to_datetime(df_inventario['Fecha_Ultima_Reposicion'])
df_usuarios['Fecha_Registro'] = pd.to_datetime(df_usuarios['Fecha_Registro'])

# 2.2 Calculamos el total de ventas por cliente
ventas_por_cliente = df_facturas.groupby('ID_Cliente')['Total'].sum().reset_index()
ventas_por_cliente = ventas_por_cliente.merge(df_usuarios[['ID_Cliente', 'Nombre', 'Apellido']], on='ID_Cliente')
print("\nTotal de ventas por cliente:")
print(ventas_por_cliente)

# 2.3 Calculamos el producto más vendido
producto_mas_vendido = df_facturas.groupby('ID_Articulo')['Cantidad'].sum().reset_index()
producto_mas_vendido = producto_mas_vendido.merge(df_inventario[['ID_Articulo', 'Nombre_Articulo']], on='ID_Articulo')
producto_mas_vendido = producto_mas_vendido.sort_values('Cantidad', ascending=False)
print("\nProducto más vendido:")
print(producto_mas_vendido.head(1))

# 2.4 Calculamos el stock actual
df_inventario['Stock_Actual'] = df_inventario['Stock'] - df_facturas.groupby('ID_Articulo')['Cantidad'].sum()
print("\nStock actual:")
print(df_inventario[['ID_Articulo', 'Nombre_Articulo', 'Stock', 'Stock_Actual']])

# 2.5 Analizamos las ventas por tipo de cliente
df_facturas_con_tipo = df_facturas.merge(df_usuarios[['ID_Cliente', 'Tipo_Cliente']], on='ID_Cliente')
ventas_por_tipo = df_facturas_con_tipo.groupby('Tipo_Cliente')['Total'].sum()
print("\nVentas por tipo de cliente:")
print(ventas_por_tipo)

# 2.6 Análisis de ventas por día
ventas_por_dia = df_facturas.groupby('Fecha')['Total'].sum().reset_index()
ventas_por_dia = ventas_por_dia.sort_values('Fecha')
print("\nVentas por día:")
print(ventas_por_dia)

# Paso 3: Carga (Load)
# Guardamos los resultados procesados en S3
write_csv_to_s3(ventas_por_cliente, 'ventas_por_cliente.csv')
write_csv_to_s3(ventas_por_dia, 'ventas_por_dia.csv')

print("\nProceso ETL completado. Los resultados han sido guardados en el bucket S3 en la carpeta 'datos-procesados'.")
