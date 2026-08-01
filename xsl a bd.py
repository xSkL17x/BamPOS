import os
import sqlite3
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def conectar_db():
    """Conecta a la base de datos y aplica configuraciones PRAGMA."""
    if not os.path.exists('PT/pts.db'):
        verificar_carpeta_y_archivo()

    conn = sqlite3.connect('PT/pts.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")

    return conn, cursor

def seleccionar_archivo():
    """Abre un cuadro de diálogo para seleccionar un archivo Excel."""
    Tk().withdraw()  # Oculta la ventana principal de Tkinter
    archivo = askopenfilename(filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
    return archivo



def importar_a_db():
    archivo_excel = seleccionar_archivo()
    
    if archivo_excel:
        conn, cursor = conectar_db()

        # Leer el archivo Excel
        xls = pd.ExcelFile(archivo_excel)

        # Lista de tablas a importar
        tablas = ['productos', 'entradas', 'categorias', 'salidas']

        # Encabezados esperados
        encabezados = {
            'productos': ['id', 'nombre', 'categoria', 'precio_compra', 'precio_venta', 'precio_minimo_venta', 'ganancia', 'stock_minimo', 'stock_actual', 'visible', 'nota', 'ruta_imagen', 'usuario', 'dispositivos'],
            'entradas': ['id_transaccion', 'id', 'nombre', 'categoria', 'cantidad', 'precio_compra', 'fecha', 'usuario', 'dispositivos'],
            'categorias': ['id', 'nombre'],
            'salidas': ['id_venta', 'fecha', 'id_producto', 'nombre', 'categoria', 'precio_venta', 'cantidad', 'ganancia_total', 'cliente', 'estado', 'n_factura', 'usuario', 'dispositivos']
        }

        for tabla in tablas:
            if tabla in xls.sheet_names:
                # Leer la hoja correspondiente a la tabla
                df = pd.read_excel(xls, sheet_name=tabla)

                # Convertir encabezados a minúsculas
                df.columns = df.columns.str.lower()

                # Verificar si los encabezados coinciden con los de la base de datos
                if not all(col in df.columns for col in encabezados[tabla]):
                    print(f"Los encabezados de la hoja '{tabla}' no coinciden con los de la base de datos. No se importarán los datos.")
                    continue

                # Convertir columnas a los tipos adecuados
                if tabla == 'productos':
                    df['id'] = df['id'].astype(str)  # Convertir 'id' a texto
                    df['precio_compra'] = pd.to_numeric(df['precio_compra'], errors='coerce').fillna(0)  # Convertir a REAL
                    df['precio_venta'] = pd.to_numeric(df['precio_venta'], errors='coerce').fillna(0)
                    df['precio_minimo_venta'] = pd.to_numeric(df['precio_minimo_venta'], errors='coerce').fillna(0)
                    df['ganancia'] = pd.to_numeric(df['ganancia'], errors='coerce').fillna(0)
                    df['stock_minimo'] = pd.to_numeric(df['stock_minimo'], errors='coerce').fillna(0).astype(int)
                    df['stock_actual'] = pd.to_numeric(df['stock_actual'], errors='coerce').fillna(0).astype(int)
                    df['visible'] = df['visible'].fillna('')  # Asegurar que esté como texto

                elif tabla == 'entradas':
                    df['id_transaccion'] = df['id_transaccion'].astype(str)
                    df['id'] = df['id'].astype(str)  # Convertir 'id' a texto
                    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
                    df['precio_compra'] = pd.to_numeric(df['precio_compra'], errors='coerce').fillna(0)

                elif tabla == 'salidas':
                    df['id_venta'] = df['id_venta'].astype(str)
                    df['id_producto'] = df['id_producto'].astype(str)  # Convertir 'id_producto' a texto
                    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
                    df['precio_venta'] = pd.to_numeric(df['precio_venta'], errors='coerce').fillna(0)
                    df['ganancia_total'] = pd.to_numeric(df['ganancia_total'], errors='coerce').fillna(0)

                elif tabla == 'categorias':
                    df['id'] = df['id'].astype(str)  # Convertir 'id' a texto

                # Verificar si la tabla existe en la base de datos
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}';")
                if cursor.fetchone() is None:
                    # Crear la tabla si no existe
                    df.head(0).to_sql(tabla, conn, if_exists='replace', index=False)

                # Insertar datos en la tabla, sobrescribiendo si existe
                df.to_sql(tabla, conn, if_exists='replace', index=False)

        # Cerrar la conexión
        conn.close()
        print("Datos importados correctamente.")
    else:
        print("No se seleccionó ningún archivo.")





if __name__ == "__main__":
    importar_a_db()
