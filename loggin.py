import os
import logging
from logging.handlers import TimedRotatingFileHandler

# Variable para verificar si el logger ya fue configurado
logger_configurado = False
logger_auditoria_configurado = False  # o True, dependiendo de tu lógica

carpeta_pt = 'PT/logs'

# Configuración del logger
def configurar_logger():
    global logger_configurado
    
    if logger_configurado:
        return  # Si ya está configurado, salir de la función

    if not os.path.exists(carpeta_pt):
        os.makedirs(carpeta_pt)

    # Crear un manejador que rota el log cada día
    handler_diario = TimedRotatingFileHandler(
        os.path.join(carpeta_pt, 'log_diario.log'),
        when='D',        # Rota el archivo diario
        interval=1,      # Cada día
        backupCount=0    # Sin mantener backups
    )

    # Crear un manejador que rota el log cada semana
    handler_semanal = TimedRotatingFileHandler(
        os.path.join(carpeta_pt, 'log_semanal.log'),
        when='W0',       # Rota el archivo semanal (0 = Lunes)
        interval=1,      # Cada semana
        backupCount=0    # Sin mantener backups
    )

    # Configuración del formato del log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler_diario.setFormatter(formatter)
    handler_semanal.setFormatter(formatter)

    # Configuración del logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler_diario)
    logger.addHandler(handler_semanal)

    logger_configurado = True  # Marcar que el logger ha sido configurado

# Función para agregar un mensaje al log
def agregar_log(mensaje):
    logging.info(mensaje)



def configurar_logger_auditoria():
    global logger_auditoria_configurado
    
    if logger_auditoria_configurado:
        return 

    if not os.path.exists(carpeta_pt):
        os.makedirs(carpeta_pt)

    # Crear un manejador para el log de auditoría sin rotación
    handler = logging.FileHandler(os.path.join(carpeta_pt, 'auditoria.log'))
    
    # Configuración del formato del log de auditoría
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Configuración del logger de auditoría
    logger_auditoria = logging.getLogger('auditoria')
    logger_auditoria.setLevel(logging.INFO)
    logger_auditoria.addHandler(handler)

    logger_auditoria_configurado = True  # Marcar que el logger de auditoría ha sido configurado

def agregar_log_auditoria(mensaje):
    logger_auditoria = logging.getLogger('auditoria')
    logger_auditoria.info(mensaje)