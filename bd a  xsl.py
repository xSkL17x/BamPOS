import os
import sqlite3
import pandas as pd

def conectar_db():
    """Conecta a la base de datos y aplica configuraciones PRAGMA."""
    # Verificar la existencia de la base de datos y crearla si no existe


    # Conectar a la base de datos
    conn = sqlite3.connect('PT/pts.db')
    cursor = conn.cursor()

    # Aplicar configuraciones PRAGMA
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")  # Ajusta según sea necesario

    return conn, cursor

def exportar_a_excel():
    # Conectar a la base de datos
    conn, cursor = conectar_db()
    
    # Nombres de las tablas que se van a exportar
    tablas = ['productos', 'entradas', 'categorias', 'salidas']
    
    # Crear un diccionario para almacenar DataFrames
    dataframes = {}
    
    # Obtener los DataFrames de cada tabla
    for tabla in tablas:
        # Verificar si la tabla existe
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}';")
        if cursor.fetchone():
            # Leer la tabla en un DataFrame
            df = pd.read_sql_query(f"SELECT * FROM {tabla};", conn)
            dataframes[tabla] = df
    
    # Cerrar la conexión
    conn.close()
    
    # Crear un archivo Excel
    with pd.ExcelWriter('exportado.xlsx', engine='openpyxl') as writer:
        for nombre, df in dataframes.items():
            df.to_excel(writer, sheet_name=nombre, index=False)

if __name__ == "__main__":
    exportar_a_excel()
