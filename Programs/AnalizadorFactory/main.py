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

REINTENTOS = {}
FACTORIAS_CORDONES = {
    "Cam1Mod1": AnalizadorCordonesCam1Mod1Factory(),
    "Cam1Mod2": AnalizadorCordonesCam1Mod2Factory(),
    "Cam2Mod1": AnalizadorCordonesCam2Mod1Factory(),
    "Cam2Mod2": AnalizadorCordonesCam2Mod2Factory()
}

def procesar_archivo(path_json, logger):

    logger.log("#################### INICIO DE NUEVO ANÁLISIS ####################")
    fichero = JsonFichero(path_json, logger)

    # Copiar y leer JSON de entrada
    fichero.leer()

    # Analizar cámaras
    if not fichero.cam1 or not fichero.cam2:
        raise ValueError("Error de configuración de cámaras en fichero json")

    # CAM 1
    modelo = str(fichero.modelo)
    tipo = f"Cam1Mod{modelo}"
    factoria = FACTORIAS_CORDONES[tipo]
    config = settings.CONFIGURACIONES["camara1"][modelo]
    logger.log("------ Inicio de análisis cámara 1 ------")
    manager = AnalisisManager(factoria, config, fichero.path_img_cam1, logger, fichero)
    fichero.res_cam1 = manager.ejecutar()

    # CAM 2
    modelo = str(fichero.modelo)
    tipo = f"Cam2Mod{modelo}"
    factoria = FACTORIAS_CORDONES[tipo]
    config = settings.CONFIGURACIONES["camara2"][modelo]
    logger.log("------ Inicio de análisis cámara 2 ------")
    manager = AnalisisManager(factoria, config, fichero.path_img_cam2, logger, fichero)
    fichero.res_cam2 = manager.ejecutar()

    # Guardar JSON de salida (usa self.res_cam1 / self.res_cam2)
    fichero.escribir()
    imagen.debug_counter = 1
    return True


def main():
    logger = Logger()
    cola = QueueManager(settings.QUEUE_DIR, logger)
    os.makedirs(settings.QUEUE_DIR_FALLOS, exist_ok=True)

    logger.log("#################### INICIO - Modo cola local ####################")
    cola_vacia_anterior = False

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
        logger.log(f"Procesando: [{siguiente}]")

        try:
            ok = procesar_archivo(siguiente, logger)
        except Exception as e:
            # Se registra detalle y se planifica reintento o mover a fallos
            logger.log(f"Error durante el análisis: {e}")
            logger.log(traceback.format_exc())
            ok = False

        if ok:
            logger.log(f"Análisis completado correctamente. Eliminando: {siguiente}")
            logger.log("#################### Análisis completo ####################")
            cola.remove(siguiente)  # eliminar con reintentos
            REINTENTOS.pop(siguiente, None)
        else:
            # reintentos
            REINTENTOS[siguiente] = REINTENTOS.get(siguiente, 0) + 1
            logger.log(f"Reintento #{REINTENTOS[siguiente]} por fallo de análisis: [{siguiente}]")

            if REINTENTOS[siguiente] >= settings.MAX_REINTENTOS:
                fallo_dest = os.path.join(settings.QUEUE_DIR_FALLOS, os.path.basename(siguiente))
                try:
                    shutil.move(siguiente, fallo_dest)
                    logger.log(f"Movido a fallos: [{siguiente}] -> [{fallo_dest}]")
                except Exception as move_err:
                    logger.log(f"No se pudo mover a fallos: {move_err}")
                REINTENTOS.pop(siguiente, None)
            else:
                time.sleep(5)  # espera antes de reintentar

if __name__ == "__main__":
    main()
