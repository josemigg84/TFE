import datetime as dt
import threading
import settings
from camara import Camara

class CaptureManager:
    def __init__(self, capture_dir, logger):

        camaras = []
        for i, url in enumerate(settings.CAMERAS_RTSP, start=1):
            cam = Camara(num=i, rtsp_url=url, logger=logger)
            camaras.append(cam)

        self.camaras = camaras
        self._capture_dir = capture_dir
        self._logger = logger

    def capturar_todo(self, pin, skid, fecha_hora):

        threads = []
        for cam in self.camaras:
            hilo = threading.Thread( target=cam.guardar_captura, args=(pin, skid, self._capture_dir, fecha_hora), daemon=True)
            hilo.start()
            threads.append(hilo)

        for hilo in threads:
            hilo.join()

        self._logger.log("Hilos finalizados")



