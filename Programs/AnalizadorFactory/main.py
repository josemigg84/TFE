import os
import time
import shutil
import traceback
from analizador_factorias_concretas import (AnalizadorCordonesCam1Mod1Factory,AnalizadorCordonesCam1Mod2Factory,AnalizadorCordonesCam2Mod1Factory,AnalizadorCordonesCam2Mod2Factory)
from queue_manager import QueueManager
from json_fichero import JsonFichero
from manager import AnalisisManager
from logger import Logger
import imagen
import settings

FACTORIAS_CORDONES = {      # factorias según cámara y modelo
    "Cam1Mod1": AnalizadorCordonesCam1Mod1Factory(),
    "Cam1Mod2": AnalizadorCordonesCam1Mod2Factory(),
    "Cam2Mod1": AnalizadorCordonesCam2Mod1Factory(),
    "Cam2Mod2": AnalizadorCordonesCam2Mod2Factory()
}

# lee un fichero JSON y ejecuta el análisis de las dos cámaras, para guardar un JSON con el resultado
def procesar_archivo(path_json, logger):

    logger.log("#################### INICIO DE NUEVO ANÁLISIS ####################")
    fichero = JsonFichero(path_json, logger)        # crear objeto JsonFichero con el path

    # Copiar y leer JSON de entrada
    fichero.leer()

    # Analizar cámaras
    if not fichero.cam1 or not fichero.cam2:
        raise ValueError("Error de configuración de cámaras en fichero json")       # elevar la excepción al main.py

    # CAM 1
    modelo = str(fichero.modelo)
    tipo = f"Cam1Mod{modelo}"
    factoria = FACTORIAS_CORDONES[tipo]                         # tipo de factoría concreta según la cámara y modelo
    config = settings.CONFIGURACIONES["camara1"][modelo]        #cargar la configuración de settings según la cámara y modelo
    logger.log("------ Inicio de análisis cámara 1 ------")
    manager = AnalisisManager(factoria, config, fichero.path_img_cam1, logger, fichero)     # crear el AnalisisManager
    fichero.res_cam1 = manager.ejecutar()               # ejecutarlom guardando el resultado en el atributo res_cam1 del fichero

    # CAM 2
    modelo = str(fichero.modelo)
    tipo = f"Cam2Mod{modelo}"
    factoria = FACTORIAS_CORDONES[tipo]                         # tipo de factoría concreta según la cámara y modelo
    config = settings.CONFIGURACIONES["camara2"][modelo]        #cargar la configuración de settings según la cámara y modelo
    logger.log("------ Inicio de análisis cámara 2 ------")
    manager = AnalisisManager(factoria, config, fichero.path_img_cam2, logger, fichero)     # crear el AnalisisManager
    fichero.res_cam2 = manager.ejecutar()               # ejecutarlom guardando el resultado en el atributo res_cam1 del fichero

    # Guardar JSON de salida (usa self.res_cam1 / self.res_cam2)
    fichero.escribir()
    imagen.debug_counter = 1        # variable para nombrar las imágenes de la carpeta debug
    return True


def main():
    logger = Logger()                                           # crear logger
    cola = QueueManager(settings.QUEUE_DIR, logger)             # crear la cola FIFO con el directorio
    os.makedirs(settings.QUEUE_DIR_FALLOS, exist_ok=True)       # crear la carpeta de fallos si no existe

    logger.log("#################### INICIO - Modo cola local ####################")
    cola_vacia_anterior = False                         # variable para escribir una sola vez en el log, cola vacía, esperando nuevos archivos

    # Variables para reintentos
    archivo_actual = None
    contador_reintentos = 0

    while True:
        siguiente = cola.get_next()         # obtener siguiente archivo

        if not siguiente:
            if not cola_vacia_anterior:
                logger.log("Cola vacía. Esperando nuevos archivos...")
                cola_vacia_anterior = True
            time.sleep(0.5)
            continue
        else:
            cola_vacia_anterior = False

        # Al cambiar el archivo, reiniciar contador
        if siguiente != archivo_actual:
            archivo_actual = siguiente
            contador_reintentos = 0

        # si se llega hasta aquí es que hay ficheros en la cola FIFO
        logger.log(f"Quedan {cola.count()} archivos en la cola.")
        logger.log(f"Procesando: [{siguiente}]")

        try:
            ok = procesar_archivo(siguiente, logger)        # llamar a procesar, guardar en ok el resultado booleano
        except Exception as e:
            # Se registra detalle y se planifica reintento o mover a fallos
            logger.log(f"Error durante el análisis: {e}")
            logger.log(traceback.format_exc())
            ok = False

        if ok:      # si el resultado ha sido ok
            logger.log(f"Análisis completado correctamente. Eliminando: {siguiente}")
            logger.log("#################### Análisis completo ####################")
            cola.remove(siguiente)  # eliminar con reintentos
            archivo_actual = None       # si se ha eliminado, inicializar
            contador_reintentos = 0     # si se ha eliminado, inicializar
        else:
            # reintentos
            contador_reintentos += 1    # si falla, aumentan los reintentos
            logger.log(f"Reintento #{contador_reintentos} por fallo de análisis: [{siguiente}]")

            if contador_reintentos >= settings.MAX_REINTENTOS:      # si el numero de reintentos es mayor que el máximo
                fallo_dest = os.path.join(settings.QUEUE_DIR_FALLOS, os.path.basename(siguiente))
                try:
                    shutil.move(siguiente, fallo_dest)          # se mueve el fichero a la carpeta de fallos
                    logger.log(f"Movido a fallos: [{siguiente}] -> [{fallo_dest}]")
                except Exception as move_err:
                    logger.log(f"No se pudo mover a fallos: {move_err}")
                archivo_actual = None       #inicializar variable
                contador_reintentos = 0     #inicializar variable
            else:
                time.sleep(5)  # espera antes de reintentar

if __name__ == "__main__":
    main()
