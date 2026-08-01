#cargardatos.py
import sqlite3

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from datos import verificar_contenido_productos_db, conectar_db, conectar_db_config
from loggin import configurar_logger, agregar_log
from kivy.uix.screenmanager import Screen

from datetime import datetime

# cargardatos.py
products_screen = None
admin_screen = None  


def obtener_productos_por_categoria():
    try:
        # Conectar a la base de datos utilizando conectar_db
        conn, cursor = conectar_db()  # Llama a la función conectar_db()

        # Consultar las categorías
        cursor.execute("SELECT DISTINCT categoria FROM productos")
        categorias = cursor.fetchall()

        productos_por_categoria = {}

        for categoria in categorias:
            cat_name = categoria[0]
            # Obtener los productos de cada categoría, ordenados por nombre
            cursor.execute("SELECT id, nombre, precio_venta, ruta_imagen, nota, stock_actual , precio_minimo_venta, precio_compra FROM productos WHERE categoria=? AND visible='SI' ORDER BY LOWER(nombre)", (cat_name,))
            productos = cursor.fetchall()
            productos_por_categoria[cat_name] = productos

        return productos_por_categoria

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        verificar_contenido_productos_db()
        return {}
    

def obtener_productos_por_categoria_con_stock():
    try:
        conn, cursor = conectar_db()  # Llama a la función conectar_db()
        cursor.execute("SELECT DISTINCT categoria FROM productos")
        categorias = cursor.fetchall()
        productos_por_categoria = {}
        for categoria in categorias:
            cat_name = categoria[0]
            cursor.execute("SELECT id, nombre, precio_venta, ruta_imagen, nota, stock_actual, precio_minimo_venta, precio_compra, categoria FROM productos WHERE categoria=? AND visible='SI' AND stock_actual > 0 ORDER BY LOWER(nombre)", (cat_name,))

            productos = cursor.fetchall()
            productos_por_categoria[cat_name] = productos
        return productos_por_categoria
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        verificar_contenido_productos_db()
        return {}





###################################################################ADMINISTRAR
def cargar_productos_administrar_lat_entradas():
    try:
        conn, cursor = conectar_db()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos';")
        if not cursor.fetchone():
            return []
        cursor.execute("""
            SELECT id, nombre, categoria, precio_compra, precio_venta, stock_actual, nota, ruta_imagen 
            FROM productos 
            WHERE UPPER(visible) = 'SI' 
            ORDER BY LOWER(categoria), stock_actual DESC
        """)
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        agregar_log(f"Error al cargar productos: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()



def cargar_productos_administrar():
    try:
        conn, cursor = conectar_db()
        # Comprobar si la tabla 'productos' existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos';")
        if not cursor.fetchone():
            return []

        # Seleccionar productos visibles, agrupados por categoría y ordenados por nombre
        cursor.execute("""
            SELECT id, nombre, categoria, precio_compra, precio_venta, stock_actual, nota, ruta_imagen 
            FROM productos 
            WHERE UPPER(visible) = 'SI' 
            ORDER BY LOWER(categoria), LOWER(nombre)
        """)
        productos = cursor.fetchall()

        return productos
    except Exception as e:
        agregar_log(f"Error al cargar productos: {e}")  # Loguear el error
        return []
    finally:
        if 'conn' in locals():
            conn.close()



def cargar_entradas_administrar():
    try:
        conn, cursor = conectar_db()

        # Verificar si la tabla 'entradas' existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entradas';")
        if not cursor.fetchone():
            return []

        cursor.execute("SELECT id_transaccion, id, nombre, categoria, cantidad, precio_compra, fecha, usuario, dispositivos FROM entradas ORDER BY fecha DESC")
        entradas = cursor.fetchall()

        return entradas
    except Exception as e:
        agregar_log(f"Error al cargar entradas: {e}")  # Mensaje de error
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def cargar_salidas_administrar():
    try:
        conn, cursor = conectar_db()

        # Verificar si la tabla 'salidas' existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='salidas';")
        if not cursor.fetchone():
            return []

        cursor.execute("SELECT id_venta, id_producto, nombre, categoria, cantidad, precio_venta,  fecha, ganancia_total, cliente, estado, n_factura,  usuario, dispositivos FROM salidas ORDER BY n_factura DESC, fecha DESC")
        salidas = cursor.fetchall()

        return salidas
    except Exception as e:
        agregar_log(f"Error al cargar salidas: {e}")  # Mensaje de error
        return []
    finally:
        if 'conn' in locals():
            conn.close()






##
def cargar_categorias_db():
    configurar_logger()
    categorias = []

    try:
        conn, cursor = conectar_db()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categorias';")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            return []

        cursor.execute("SELECT nombre FROM categorias ORDER BY LOWER(nombre)")
        categorias = cursor.fetchall()

    except Exception as e:
        agregar_log(f"Ocurrió un error al cargar las categorías: {e}")
    finally:
        cursor.close()
        conn.close()

    return categorias





####################Recargar tablas #################



#cargardatos.py
def set_products_screen(screen):
    global products_screen
    products_screen = screen

def set_admin_screen(screen):
    global admin_screen
    admin_screen = screen



def recargardatostablas(): 
    global products_screen  
    global admin_screen  
    if admin_screen:
        comprobar_y_recargar_admin_table()    
    if products_screen:
        comprobar_y_recargar_products_table()


################### Recargar Tablas separadas #############

def recargar_tabla_admin(): 
    global admin_screen
    if admin_screen:
        comprobar_y_recargar_admin_table()

def recargar_tabla_productos():
    global products_screen    
    if products_screen:
        comprobar_y_recargar_products_table()


########################### recargar tablas global ##############


def comprobar_y_recargar_admin_table():
    configurar_logger() 
    if admin_screen:
        admin_screen.recargarproductos_en_tabla()
    else:
         agregar_log("Error: admin_screen no está disponible.")

def comprobar_y_recargar_products_table():
    configurar_logger() 
    if products_screen:
        products_screen.cargar_productos()
    else:
        agregar_log("Error: products_screen no está disponible.")




############ recargar al editar #########

############ llamar esta funcion solo agregar #########
        #global products_screen  # Accede a la variable global
        #global admin_screen  # Accede a la variable global
        #recargardatostablas() recargar_productos











def obtener_usuarios_db():
    try:
        conn, cursor = conectar_db_config()
        cursor.execute("SELECT id, nombre, apellido, contrasena, rango FROM Usuarios ORDER BY CASE rango WHEN 'owner' THEN 1 WHEN 'admin' THEN 2 ELSE 3 END")
        usuarios = cursor.fetchall()
        return usuarios
    except sqlite3.Error as e:
        print(f"Error al obtener usuarios de la base de datos: {e}")
        return []
    finally:
        if conn:
            conn.close()
