import os
from dotenv import load_dotenv

load_dotenv()  # busca el archivo .env en el directorio

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "images")
PATH_GUARDAR_JSON = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),"data","App","Local","ordenes","fifo_grabar_analizar") # ir a dos carpetas anteriores del directorio actual (quitar: programs/Analizador) y añadirle: temp/App/Local/Data/orders/analyzed/
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "logs")

# CONFIGURACIÓN PLC
PLC_IP = os.getenv('PLC_IP')
PLC_RACK = 0
PLC_SLOT = 3            #debe ser =2 para S7-300, =3 para S7-400
DB_NUM = 1         #configuración del número de DB y bytes para leer info del PLC
#DB_NUM = 1451
INICIO_BYTES = 0
TOTAL_BYTES = 18
TRIGGER_BYTE = 0
TRIGGER_BIT = 0
PIN_OFFSET = 2
SKID_OFFSET = 6
MODELO_OFFSET = 8
APP_DATETIME_OFFSET = 10
ACK_BYTE = 1
ACK_BIT = 0
DELAY = 0.05        #lee del PLC cada 50ms

# CONFIGURACIÓN CÁMARAS
USUARIO = os.getenv('USUARIO')
PASSWORD = os.getenv('PASSWORD')
IP_CAM_1 = os.getenv('IP_CAM_1')
IP_CAM_2 = os.getenv('IP_CAM_2')

CAMERAS_RTSP = [
    f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAM_1}/Streaming/Channels/101",
    f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAM_2}/Streaming/Channels/101",
]
