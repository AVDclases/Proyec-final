import pandas as pd
import sqlite3
import os
import numpy as np

#Solicito la ruta donde voy mapear traer la base de datos
def mapear_datos(nombre_bd, formato): 
    carpeta = os.path.dirname(__file__)
    db_path = os.path.join(carpeta, '..', 'data', f'{nombre_bd}{formato}')
    return db_path

#Le solicito me traiga las tablas de la Base de datos y me lo guarde como dicionario
def cargar_datos(ruta_archivo):
    conn = sqlite3.connect(ruta_archivo)
    
    dataframes = {}
    
    tablas = pd.read_sql('SELECT name FROM sqlite_master WHERE type = "table"', conn)
    
    for tabla in tablas['name']:
        dataframes[tabla] = pd.read_sql(f'SELECT * FROM "{tabla}"', conn)
    
    conn.close()   
    
    return dataframes

#Muestra la ruta para almacenar la base de datos
ruta = mapear_datos("Northwind_small",".sqlite")

#caraga los datos en forma de diccionario
data = cargar_datos(ruta)

#tablas de las bases de datos
ordenes = data["Order"]
cliente = data["Customer"]
categoria = data["Category"]
detalles_ordenes = data["OrderDetail"]
producto = data["Product"]
empleado = data["Employee"]
region = data["Region"]
provedor = data["Supplier"]
territorio = data["Territory"]

#Unir tablas para obtener la data
datos_productos = pd.merge(ordenes, cliente, left_on="CustomerId", right_on="Id")

detalle = pd.merge(datos_productos, detalles_ordenes, left_on="Id_x", right_on="OrderId")

#multiplicar precio por cantidad
detalle["Total"] = detalle["UnitPrice"]*detalle["Quantity"]

#Agrupar país con la suma de totales y crear columna 
ventas = detalle.groupby("ShipCountry")["Total"].sum().reset_index(name="Totalsales")

#ordenar por los descuentos de anera descendente
ventas_ordenadas = ventas.sort_values(by= "Totalsales", ascending= False)





