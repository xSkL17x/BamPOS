import os
import sys
import psutil
import sqlite3
import tempfile
from loggin import configurar_logger, agregar_log



directorio_actual = os.path.dirname(os.path.abspath(__file__))
pid_file = os.path.join(directorio_actual,'assets', 'app.pid')
Rutadb = 'PT/pts.db'



def obtener_ruta_assets():
    """Devuelve la ruta absoluta de la base de datos."""
    ruta_fuentes = os.path.join(directorio_actual, 'assets')
    return ruta_fuentes





def conectar_db():
    """Conecta a la base de datos y aplica configuraciones PRAGMA."""
    # Verificar la existencia de la base de datos y crearla si no existe
    if not os.path.exists(Rutadb):
        verificar_carpeta_y_archivo()

    # Conectar a la base de datos
    conn = sqlite3.connect(Rutadb)
    cursor = conn.cursor()

    # Aplicar configuraciones PRAGMA
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")  # Ajusta según sea necesario

    return conn, cursor


def conectar_db_config():
    """Conecta a la base de datos 'configuraciones.db' y aplica configuraciones PRAGMA."""
    carpeta_assets = obtener_ruta_assets()
    db_path = os.path.join(carpeta_assets, 'configuraciones.db')

    if not os.path.exists(db_path):
        crear_y_verificar_configuraciones()
        
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL;")  # Activar el modo WAL (Write-Ahead Logging)
    cursor.execute("PRAGMA synchronous=NORMAL;")  # Ajustar el nivel de sincronización según sea necesario
    print("ℹ️ Conectado a DB Configuraciones con PRAGMAs aplicados.")
    return conn, cursor

############################### crear la base de datos ###########################################


def verificar_carpeta_y_archivo():
    configurar_logger()

    carpeta_pt = 'PT'
    if not os.path.exists(carpeta_pt):
        os.makedirs(carpeta_pt)
        agregar_log(f"Se creó la carpeta '{carpeta_pt}' exitosamente.")
    
    if not os.path.exists(Rutadb):
        resultado_db = crear_y_verificar_base_datos() 
        if resultado_db != "db_lista":
            return None
    else:
        try:
            conn = sqlite3.connect(Rutadb)
            cursor = conn.cursor()
            tablas = ['productos', 'categorias', 'entradas', 'salidas', 'facturas']  # Añadida la tabla 'facturas'
            for tabla in tablas:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'")
                if cursor.fetchone() is None:
                    resultado_db = crear_y_verificar_base_datos()
                    if resultado_db != "db_lista":
                        return None
                    break
        except sqlite3.Error as e:
            return None
        finally:
            if conn:
                conn.close()

    return "verificacion_hecha"




############## Crear base de datos ################## 


def crear_y_verificar_base_datos():
    """Crea la base de datos SQLite y las tablas necesarias si no existen."""
    try:
        conn = sqlite3.connect(Rutadb)
        cursor = conn.cursor()

        # Crear tabla de productos
        cursor.execute('''CREATE TABLE IF NOT EXISTS productos (id TEXT PRIMARY KEY, nombre TEXT, categoria TEXT, 
                         precio_compra REAL, precio_venta REAL, precio_minimo_venta REAL, ganancia REAL, stock_minimo INTEGER, 
                         stock_actual INTEGER, visible TEXT, nota TEXT, ruta_imagen TEXT, usuario TEXT, dispositivos TEXT)''')

        # Crear tabla de categorías
        cursor.execute('''CREATE TABLE IF NOT EXISTS categorias (id TEXT PRIMARY KEY, nombre TEXT UNIQUE NOT NULL)''')

        # Crear tabla de entradas
        cursor.execute('''CREATE TABLE IF NOT EXISTS entradas (id_transaccion TEXT PRIMARY KEY, id TEXT, nombre TEXT, 
                         categoria TEXT, cantidad INTEGER, precio_compra REAL, fecha TEXT, usuario TEXT, dispositivos TEXT)''')

        # Crear tabla de salidas
        cursor.execute('''CREATE TABLE IF NOT EXISTS salidas (id_venta TEXT PRIMARY KEY, fecha TEXT, id_producto TEXT, 
                         nombre TEXT, categoria TEXT, precio_venta REAL, cantidad INTEGER, ganancia_total REAL, cliente TEXT, 
                         estado TEXT, n_factura TEXT, usuario TEXT, dispositivos TEXT)''')

        # Crear tabla de facturas
        cursor.execute("CREATE TABLE IF NOT EXISTS facturas (id INTEGER PRIMARY KEY, no_factura INTEGER)")


        # Crear índices para mejorar el rendimiento
        cursor.execute('''CREATE INDEX IF NOT EXISTS idx_productos_id ON productos (id)''')
        cursor.execute('''CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos (nombre)''')
        cursor.execute('''CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos (categoria)''')
        cursor.execute('''CREATE INDEX IF NOT EXISTS idx_productos_nota ON productos (nota)''')
        cursor.execute('''CREATE INDEX IF NOT EXISTS idx_entradas_id ON entradas (id)''')
        cursor.execute('''CREATE INDEX IF NOT EXISTS idx_entradas_nombre ON entradas (nombre)''')
        cursor.execute('''CREATE INDEX IF NOT EXISTS idx_entradas_categoria ON entradas (categoria)''')
        cursor.execute('INSERT OR IGNORE INTO facturas (id, no_factura) VALUES (1, 0)')


        conn.commit()
        print("ℹ️ Se creó o verificó la base de datos y las tablas necesarias.")
    except sqlite3.Error as e:
        agregar_log(f"Error al conectar a la base de datos: {e}")
    finally:
        if conn:
            conn.close()
    return "db_lista"


            ################################################################






def crear_y_verificar_configuraciones():
    carpeta_assets = obtener_ruta_assets()

    if not os.path.exists(carpeta_assets):
        os.makedirs(carpeta_assets)
    
    tablas_creadas = False  # Bandera para verificar si se crearon nuevas entradas
    try:
        conn = sqlite3.connect(os.path.join(carpeta_assets, 'configuraciones.db'))
        cursor = conn.cursor()
        
        # Crear tabla configuraciones
        cursor.execute("""CREATE TABLE IF NOT EXISTS configuraciones (accion TEXT, valor1 TEXT, valor2 TEXT, valor3 TEXT, valor4 TEXT, valor5 TEXT, PRIMARY KEY (accion, valor1));""")
        cursor.execute('''CREATE INDEX IF NOT EXISTS idx_accion_valor1 ON configuraciones (accion, valor1)''')

        # Crear tabla Usuarios con ID
        cursor.execute("""CREATE TABLE IF NOT EXISTS Usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, apellido TEXT, contrasena TEXT, rango TEXT);""")
        cursor.execute("SELECT COUNT(*) FROM Usuarios")

        if cursor.fetchone()[0] == 0:
            cursor.execute("""INSERT INTO Usuarios (nombre, apellido, contrasena, rango) VALUES (?, ?, ?, ?)""", ("admin", "", "", "owner"))
            tablas_creadas = True  # Se creó una nueva entrada en Usuarios

        # Comprobar y crear configuraciones
        configuraciones = [
            ('version pos', '0.1', '', '', '', ' '), 
            ('remember user', 'si', 'admin', ' ', 'owner', ' '), 
            ("autologin", "no", "admin", "", "owner", ""),
            ('config negocio', 'Bam_Pos', '', '', '@gmail.com', ' '), 
            ('impresoras', 'desactivada', 'desactivada', '', '', ' ')
        ]

        for config in configuraciones:
            # Verificar si la configuración ya existe
            cursor.execute("SELECT COUNT(*) FROM configuraciones WHERE accion = ?", (config[0],))
            if cursor.fetchone()[0] == 0:  # Si la acción no existe, insertar
                cursor.execute('INSERT INTO configuraciones (accion, valor1, valor2, valor3, valor4, valor5) VALUES (?, ?, ?, ?, ?, ?)', config)
                agregar_log(f"Configuración '{config[0]}' insertada en la tabla 'configuraciones'")
                tablas_creadas = True  #

        conn.commit()
        
        # Ajustar el mensaje final
        if tablas_creadas:
            agregar_log("Tablas 'configuraciones' y 'Usuarios' creadas exitosamente.")
        
    except sqlite3.Error as e:
        agregar_log(f"Error al conectar a la base de datos: {e}")
    finally:
        if conn:
            conn.close()
    return "db_Configuraciones_lista"









############### verificaciones en tabla ##################    


def verificar_contenido_productos_db():
    """Verifica el contenido de la base de datos SQLite y limpia entradas inválidas."""
    print("ℹ️ Verificando contenido de la base de datos 'pts.db'")
    
    # Verificar si la base de datos existe
    if not os.path.exists(Rutadb):
        verificar_carpeta_y_archivo()  # Llamar a la función para crear la carpeta y la base de datos

    conn, cursor = conectar_db()
    try:
        cursor.execute("BEGIN;")  # Iniciar una transacción para leer
        cursor.execute("SELECT * FROM productos")
        rows = cursor.fetchall()

        print(f"ℹ️ Total de registros encontrados: {len(rows)}")

        filas_validas = []
        filas_invalidas = []  # Lista para almacenar filas inválidas
        for row in rows:
            if len(row) == 14:  # Verificar que la fila tenga el número correcto de columnas
                valid_row = list(row)  # Hacer una copia de la fila
                is_valid = True  # Suponemos que la fila es válida

                for i in [3, 4, 5, 6, 7, 8]:  # índices de precio_compra, precio_venta, precio_minimo_venta, ganancia, stock_minimo, stock_actual
                    if valid_row[i] is None or not isinstance(valid_row[i], (int, float)):
                        print(f"⚠️ Fila inválida encontrada: {row}. Se reemplazará el valor en el índice {i} con 0.")
                        valid_row[i] = 0  # Reemplazar con 0 si no es válido
                        is_valid = False  # Marcar como inválida

                if is_valid:
                    filas_validas.append(tuple(valid_row))  # Agregar fila válida
                else:
                    filas_invalidas.append(row)  # Agregar fila inválida a la lista

        print(f"ℹ️ Total de filas válidas: {len(filas_validas)}")
        print(f"ℹ️ Total de filas inválidas: {len(filas_invalidas)}")

        # Si hay filas inválidas, limpiar la tabla
        if filas_invalidas:
            cursor.execute("DELETE FROM productos")  # Eliminar todas las filas
            print("✔️ Se han eliminado filas inválidas de la tabla 'productos'.")

            # Insertar filas válidas
            cursor.executemany("INSERT INTO productos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", filas_validas)
            print(f"✔️ {len(filas_validas)} filas válidas han sido insertadas en la base de datos.")
        else:
            print("✔️ No se encontraron filas inválidas. No se realizaron cambios en la tabla.")

        conn.commit()

    except sqlite3.Error as e:
        print(f"⚠️ Ocurrió un error al verificar el contenido: {e}")
        conn.rollback()  # Revierte si hay un error
    finally:
        conn.close()

































# Funciones para la tabla de categorías


def agregar_categoria(nombre):
    """Agrega una nueva categoría a la base de datos."""
    conn, cursor = conectar_db()
    
    try:
        cursor.execute('''
            INSERT INTO categorias (nombre) VALUES (?)
        ''', (nombre,))
        conn.commit()
        print(f"Categoría '{nombre}' agregada con éxito.")
    except sqlite3.IntegrityError:
        print(f"La categoría '{nombre}' ya existe.")
    except sqlite3.Error as e:
        print(f"Ocurrió un error al agregar la categoría: {e}")
    finally:
        conn.close()

def listar_categorias():
    """Lista todas las categorías en la base de datos."""
    conn, cursor = conectar_db()

    try:
        cursor.execute("SELECT * FROM categorias")
        categorias = cursor.fetchall()
        print("Lista de categorías:")
        for categoria in categorias:
            print(f"ID: {categoria[0]}, Nombre: {categoria[1]}")
    except sqlite3.Error as e:
        print(f"Ocurrió un error al listar las categorías: {e}")
    finally:
        conn.close()





pid_file = os.path.join(tempfile.gettempdir(), "posbyskl.pid")
def verificar_instancia():    
    pid = os.getpid()    
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as file:
                existing_pid = int(file.read().strip())
                if psutil.pid_exists(existing_pid):
                    print("La aplicación ya está en ejecución.")
                    sys.exit()
        except (ValueError, OverflowError, OSError):
            print("El archivo PID está corrupto o no se puede abrir. Eliminando archivo PID.")
            eliminar_pid()

    with open(pid_file, 'w') as file:
        file.write(str(pid))

def eliminar_pid():
    try:
        os.remove(pid_file)
    except OSError as e:
        agregar_log(f"No se pudo eliminar el archivo PID: {e}")









#################################################     Funcion para agregar a inportar Base de datos desde archivo                  ###########################################################################################################        
def cargar_categorias_a_db():
    try:
        # Conectar a la base de datos utilizando conectar_db
        conn, cursor = conectar_db()  # Llama a la función conectar_db()

        # Consultar las categorías de la tabla productos
        cursor.execute("SELECT DISTINCT categoria FROM productos")
        categorias = cursor.fetchall()

        # Extraer los nombres de las categorías en una lista
        categorias_lista = [categoria[0] for categoria in categorias]

        # Insertar las categorías en la tabla categorias
        for categoria in categorias_lista:
            # Verificar si la categoría ya existe
            cursor.execute("SELECT COUNT(*) FROM categorias WHERE nombre=?", (categoria,))
            existe = cursor.fetchone()[0]

            if existe == 0:  # Si la categoría no existe, se inserta
                cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (categoria,))
                print(f"Categoría '{categoria}' agregada a la base de datos.")
            else:
                print(f"Categoría '{categoria}' ya existe en la base de datos.")

        # Confirmar los cambios y cerrar la conexión
        conn.commit()
        cursor.close()
        conn.close()

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")

