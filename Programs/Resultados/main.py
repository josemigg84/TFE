import time
import os
import shutil
from mysql.connector import InterfaceError, OperationalError
from queue_manager import QueueManager
from grabar_carroceria import CarroceriaDBWriter
from logger import Logger
from settings import QUEUE_DIR, MAX_REINTENTOS, CARPETA_FALLOS, DB_CONFIG


reintentos = {}

def main():
    logger = Logger()
    cola = QueueManager(QUEUE_DIR, logger)
    escritor = CarroceriaDBWriter(DB_CONFIG, logger=logger)
    cola_vacia_anterior = False

    os.makedirs(CARPETA_FALLOS, exist_ok=True)

    while True:
        siguiente = cola.get_next()

        if not siguiente:
            if not cola_vacia_anterior:
                logger.log("Cola vacía. Esperando nuevos archivos...")
                cola_vacia_anterior = True
            time.sleep(0.5)
            continue
        else:
            cola_vacia_anterior = False

        logger.log(f"Quedan {cola.count()} archivos en la cola.")
        logger.log(f"Procesando archivo: [{siguiente}]")

        try:
            escritor.insertar_desde_json(siguiente)
            cola.remove(siguiente)
            reintentos.pop(siguiente, None)

        except (InterfaceError, OperationalError) as e:
            logger.log(f"Error de conexión a la BBDD: {e}")
            logger.log("Reintentando más tarde sin mover archivo...")
            time.sleep(10)

        except Exception as e:
            reintentos[siguiente] = reintentos.get(siguiente, 0) + 1
            logger.log(f"Reintento #{reintentos[siguiente]} por fallo de inserción: [{siguiente}]")

            if reintentos[siguiente] >= MAX_REINTENTOS:
                fallo_dest = os.path.join(CARPETA_FALLOS, os.path.basename(siguiente))
                shutil.move(siguiente, fallo_dest)
                logger.log(f"Archivo movido a fallos: [{siguiente}]")
                reintentos.pop(siguiente)
            else:
                time.sleep(5)

if __name__ == "__main__":
    main()
