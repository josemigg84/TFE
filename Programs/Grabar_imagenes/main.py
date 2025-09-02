import os
import time
import datetime as dt
from logger import Logger
from cliente_plc import PLCClient
from manager_capturas import CaptureManager
from json_fichero import JsonFichero
import settings


def main():
    # crear Logger
    logger = Logger()

    # crear gestor de captura
    gestor = CaptureManager(settings.CAPTURE_DIR, logger)

    # Flanco del trigger
    last_trigger: bool = False

    #Crear PLC y conectar
    plc = PLCClient(logger)
    plc.connect()
    logger.log("Esperando nueva carrocería desde el PLC...")
    while True:
        salir = False
        try:
            data = plc.leer()         #leer del PLC
        except (ValueError, RuntimeError, OSError) as e:
            time.sleep(0.5)
            logger.log(f"Lectura PLC falló: {e}. Reintentando...")
            time.sleep(0.5)
            plc.reconnect(delay_s=2.0)  # <- mismo objeto, estado limpio
            time.sleep(0.5)
            continue

        trigger = bool(data["trigger"])
        pin = (data["pin"])
        skid = (data["skid"])
        modelo = int(data["modelo"])
        fecha_app = data["fecha_app"]

        if trigger and not last_trigger:
            logger.log("######## INICIO NUEVO PROCESO ########")
            logger.log(f"Número PIN desde PLC: {pin}")
            logger.log(f"Número SKID desde PLC: {skid}")
            logger.log(f"MODELO desde PLC: {modelo}")

            fh = dt.datetime.now() #misma fecha_hora para todas las cámaras y el JSON

            gestor.capturar_todo(pin=pin, skid=skid, fecha_hora= fh)
            for cam in gestor.camaras:
                if not cam.res:
                    logger.log("Alguna cámara no ha capturado la imagen correctamente, no se genera json")
                    logger.log(f"Carrocería {pin} no se revisa")
                    salir = True
                    break
            if salir:
                logger.log("Esperando nueva carrocería desde el PLC...")
                last_trigger = trigger
                continue

            logger.log("Todas las capturas de imágen finalizadas.")
            plc.escribir()                      #escribir confirmación en el PLC

            #lógica de generar json

            id_fecha = fh.strftime("%y")   #sacar los dos últimos digitos, 2025 -> 25
            datetime_app = fecha_app.strftime("%Y-%m-%d %H:%M:%S") # --> fecha de aplicación, leída desde el PLC
            datetime_gra = fh.strftime("%Y-%m-%d %H:%M:%S") # fecha actual
            db_id = int(str(pin)+id_fecha)     # pin + id_fecha, 6320001 + 25 ->  632000125

            os.makedirs(settings.PATH_GUARDAR_JSON, exist_ok=True)  #asegurar que existe el directorio donde guardar json en la cola FIFO
            # path para escribir dentro del JSON como str
            path_escribir = os.path.join("images", str(fh.year), f"{fh.month:02}", f"{fh.day:02}", str(pin))
            path_guardar = os.path.join(settings.PATH_GUARDAR_JSON, f"{pin}_in.json")

            fichero = JsonFichero(db_id, pin, skid, modelo, path_escribir, datetime_app, datetime_gra, path_guardar, logger)
            fichero.escribir()

            logger.log("Esperando nueva carrocería desde el PLC...")


        last_trigger = trigger
        time.sleep(settings.DELAY)



if __name__ == "__main__":
    main()

