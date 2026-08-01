# configs.py

import platform as sys_platform
from kivy.utils import platform as kivy_platform
from datos import conectar_db_config
from loggin import configurar_logger, agregar_log



def obtener_info_dispositivo():
    try:
        sistema = sys_platform.system()
        nombre_dispositivo = sys_platform.node()
        return f"{sistema} - {nombre_dispositivo}"
    except Exception:
        return ""



############################ Variables globales ##############
factura = '0'
def obtener_factura():
    return factura




############################ Variables globales ##############
def cargar_todas_configuraciones():
    configurar_logger()
    """Carga todas las configuraciones necesarias para la aplicación."""
    if (cargar_datos_impresion() is not None and
        cargar_datos_empresa() is not None and
        cargar_configuraciones() is not None):
        
        #imprimir_datos_configuracion()
        return "configuraciones_cargadas"
    else:
        agregar_log("error_cargando_configuraciones")
        return "error_en_carga"



 
############################ Datos empresa ##############
# Variables globales para los datos de impresión
imprimir_ticket = ''
imprimir_facturas = ''

def cargar_datos_impresion():
    global imprimir_ticket, imprimir_facturas  # Usar variables globales
    conn, cursor = conectar_db_config()

    # Cargar datos de configuración de impresión
    cursor.execute("SELECT valor1, valor2 FROM configuraciones WHERE accion = 'impresoras'")
    config = cursor.fetchone()

    if config:
        imprimir_ticket, imprimir_facturas = config

    conn.close()
    return "datos_impresion_cargados"

# Funciones para obtener estos valores
def obtener_imprimir_ticket():
    return imprimir_ticket

def obtener_imprimir_facturas():
    return imprimir_facturas



############################ Datos empresa ##############
# Variables globales para los datos de la empresa
nombre_negocio = ''
direccion_empresa = ''
telefono_empresa = ''
correo_empresa = ''


def cargar_datos_empresa():
    global nombre_negocio, direccion_empresa, telefono_empresa, correo_empresa  # Usar variables globales
    conn, cursor = conectar_db_config()
    
    # Cargar datos de la configuración del negocio
    cursor.execute("SELECT valor1, valor2, valor3, valor4 FROM configuraciones WHERE accion = 'config negocio'")
    config = cursor.fetchone()
    
    if config:
        nombre_negocio, direccion_empresa, telefono_empresa, correo_empresa = config

    conn.close()
    return "datos_empresa_cargados"

# Funciones para obtener estos valores
def obtener_nombre_negocio():
    return nombre_negocio

def obtener_direccion_empresa():
    return direccion_empresa

def obtener_telefono_empresa():
    return telefono_empresa

def obtener_correo_empresa():
    return correo_empresa

############################ Variables Configuracion ##############
# Nuevas variables globales para la versión
version_pos = ''
autologin = ''
autologin_usuario = '' 
remember_user = ''  
remember_user_usuario = '' 

def cargar_configuraciones():
    global autologin, autologin_usuario, remember_user, remember_user_usuario, version_pos  # Añadir version_pos como global
    conn, cursor = conectar_db_config() 
    
    cursor.execute("SELECT * FROM configuraciones")
    rows = cursor.fetchall()
    for row in rows:
        if row[0] == 'autologin':
            autologin = row[1]  # Columna 2
            autologin_usuario = (row[2], row[3], row[4])  # Almacena columnas 3, 4 y 5 como una tupla
        elif row[0] == 'remember user':  
            remember_user = row[1]  # Columna 2
            remember_user_usuario = row[2]  # Almacena la columna 3
        elif row[0] == 'version pos':
            version_pos = row[1]  # Columna 2 para la versión POS

    conn.close()
    return "configuraciones_cargadas"    

# Función para obtener la versión de POS
def obtener_version_pos():
    return version_pos

# Funciones existentes para obtener otros valores
def obtener_autologin():
    return autologin

def obtener_autologin_usuario():
    return autologin_usuario

def obtener_remember_user():
    return remember_user

def obtener_remember_user_usuario():
    return remember_user_usuario



############################ Variables Configuracion ##############





def imprimir_datos_configuracion():
    cargar_datos_empresa()
    cargar_datos_impresion()
    cargar_configuraciones()  
    # Datos de la empresa
    print(f"")
    print(f"")
    print("############################ Datos de la Empresa ############################")
    print(f"Nombre del Negocio: {obtener_nombre_negocio()}")
    print(f"Dirección: {obtener_direccion_empresa()}")
    print(f"Teléfono: {obtener_telefono_empresa()}")
    print(f"Correo: {obtener_correo_empresa()}")
    
    # Datos de impresión
    print("############################ Datos de Impresión ############################")
    print(f"Imprimir Ticket: {obtener_imprimir_ticket()}")
    print(f"Imprimir Facturas: {obtener_imprimir_facturas()}")
    
    # Configuraciones
    print("############################ Configuraciones ############################")
    print(f"Autologin: {obtener_autologin()}")
    print(f"Usuario Autologin: {obtener_autologin_usuario()}")
    print(f"Recuerda Usuario: {obtener_remember_user()}")
    print(f"Usuario Recuerda: {obtener_remember_user_usuario()}")
    print(f"")
    print(f"")







