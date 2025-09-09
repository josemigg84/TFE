import datetime as dt
import threading
import settings
from camara import Camara

class CaptureManager:
    def __init__(self, capture_dir, logger):

        camaras = []
        for i, url in enumerate(settings.CAMERAS_RTSP, start=1):    # crear todas las cámaras
            cam = Camara(num=i, rtsp_url=url, logger=logger)
            camaras.append(cam)                                     # las añade a cámaras

        self.camaras = camaras
        self._capture_dir = capture_dir
        self._logger = logger

    # metodo que captura de forma concurrente todas las imágenes de las cámaras creadas
    def capturar_todo(self, pin, skid, fecha_hora):

        threads = []
        for cam in self.camaras:
            # cada hilo ejecuta el metodo guardar captura del objeto Cámara
            hilo = threading.Thread( target=cam.guardar_captura, args=(pin, skid, self._capture_dir, fecha_hora), daemon=True)
            hilo.start()
            threads.append(hilo)

        for hilo in threads:
            hilo.join()

        self._logger.log("Hilos finalizados")



