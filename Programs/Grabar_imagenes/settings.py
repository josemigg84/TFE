import os
from dotenv import load_dotenv

load_dotenv()  # busca el archivo .env en el directorio

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "images")
PATH_GUARDAR_JSON = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),"data","App","Local","ordenes","fifo_grabar_analizar") # ir a dos carpetas anteriores del directorio actual (quitar: programs/Analizador) y añadirle: data/App/Local/orders/fifo_grabar_analizar/
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "logs")

# CONFIGURACIÓN PLC
PLC_IP = os.getenv('PLC_IP')
PLC_RACK = 0            # número de rack del PLC
PLC_SLOT = 3            # Slot debe ser =2 para S7-300, =3 para S7-400
DB_NUM = 1450         # configuración del número de DB y bytes para leer info del PLC
INICIO_BYTES = 0       # offset de inicio de captura de datos
TOTAL_BYTES = 18       # ancho de datos de lectura
TRIGGER_BYTE = 0        # offset del byte del trigger
TRIGGER_BIT = 0         # offset del bit del trigger
PIN_OFFSET = 2          # offset del byte del número de carrocería
SKID_OFFSET = 6         # offset del byte del número de skid
MODELO_OFFSET = 8       # offset del byte del modelo
APP_DATETIME_OFFSET = 10    # offset del byte de la fecha de aplicación
ACK_BYTE = 1        # offset del byte de escritura hacia el PLC
ACK_BIT = 0         # offset del bit de escritura hacia el PLC
DELAY = 0.05        #lee del PLC cada 50ms

# CONFIGURACIÓN CÁMARAS se lee desde .env
USUARIO = os.getenv('USUARIO')
PASSWORD = os.getenv('PASSWORD')
IP_CAM_1 = os.getenv('IP_CAM_1')
IP_CAM_2 = os.getenv('IP_CAM_2')

# lista de cámaras configuradas
CAMERAS_RTSP = [
    f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAM_1}/Streaming/Channels/101",
    f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAM_2}/Streaming/Channels/101",
]
