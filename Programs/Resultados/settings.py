import os
from dotenv import load_dotenv

load_dotenv()  # busca el archivo .env en el directorio

QUEUE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),"data","App","Local","ordenes","fifo_analizar_resultados")
CARPETA_FALLOS = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),"data","App","Local","ordenes","fifo_analizar_resultados_fallos")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "logs") #directorio para guardar logs
MAX_REINTENTOS = 3

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'port': os.getenv('PORT')
}

