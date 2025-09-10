import time
import os
import shutil
from mysql.connector import InterfaceError, OperationalError
from queue_manager import QueueManager
from grabar_carroceria import CarroceriaDBWriter
from logger import Logger
from settings import QUEUE_DIR, MAX_REINTENTOS, CARPETA_FALLOS, DB_CONFIG


def main():
    logger = Logger()   # crear el logger
    cola = QueueManager(QUEUE_DIR, logger)   # crear la cola FIFO
    escritor = CarroceriaDBWriter(DB_CONFIG, logger=logger)     # nuevo objeto para registrar el resultado del análisis en la BBDD
    cola_vacia_anterior = False        # variable para escribir una sola vez el estado de espera de nuevos ficheros JSON

    os.makedirs(CARPETA_FALLOS, exist_ok=True)      # crear la carpeta de fallos si no existe
    archivo_actual = None                           # inicializar variable de fichero actual
    contador_fallos = 0                             # inicializar variable para contar el número de reintentos del fichero actual

    while True:
        siguiente = cola.get_next()     # siguiente fichero de la cola FIFO

        if not siguiente:               # cola vacía
            if not cola_vacia_anterior:
                logger.log("Cola vacía. Esperando nuevos archivos...")
                cola_vacia_anterior = True
            time.sleep(0.5)
            continue
        else:
            cola_vacia_anterior = False

        # si pasa por aquí es que hay ficheros por procesar en la cola
        if siguiente != archivo_actual:        # al cambiar de fichero se actualizan las variables
            archivo_actual = siguiente
            contador_fallos = 0

        logger.log(f"Quedan {cola.count()} archivos en la cola.")
        logger.log(f"Procesando archivo: [{siguiente}]")

        try:
            escritor.insertar_desde_json(siguiente)     # trata de insertar los datos en la BBDD
            cola.remove(siguiente)                      # después borra el fichero
            archivo_actual = None                       # si se ha borrado el fichero, inicializar
            contador_fallos = 0                         # si se ha borrado el fichero, inicializar

        except (InterfaceError, OperationalError) as e:
            logger.log(f"Error de conexión a la BBDD: {e}")
            logger.log("Reintentando sin mover el archivo")
            time.sleep(10)

        except Exception as e:
            contador_fallos += 1
            logger.log(f"Reintento #{contador_fallos} por fallo de inserción: [{siguiente}]")

            if contador_fallos >= MAX_REINTENTOS:       # si se supera el valor de intentos máximo, mover el fichero a carpeta de fallos
                fallo_dest = os.path.join(CARPETA_FALLOS, os.path.basename(siguiente))
                shutil.move(siguiente, fallo_dest)
                logger.log(f"Archivo movido a fallos: [{siguiente}]")
                archivo_actual = None           # si se ha movido el fichero, inicializar
                contador_fallos = 0             # si se ha movido el fichero, inicializar
            else:
                time.sleep(5)       # esperar antes de volver a procesar otro intento

if __name__ == "__main__":
    main()
