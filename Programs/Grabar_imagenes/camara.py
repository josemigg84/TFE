import os
import cv2
import socket
from urllib.parse import urlparse

class Camara:
    def __init__(self, num, rtsp_url, logger):
        self._num = num
        self._rtsp_url = rtsp_url
        self._logger = logger
        self._ruta = ""
        self.res = False


    @staticmethod
    def _puerto_abierto(host, port = 554, timeout = 1.5):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def guardar_captura(self, pin, skid, capture_dir, fecha_hora):
        self.res = False

        #Comprobar si comunica la cámara
        host = urlparse(self._rtsp_url).hostname
        if host and not self._puerto_abierto(host, 554, timeout=1):
            self._logger.log(f"[Cam{self._num}] RTSP no accesible en {host}:554")
            self.res = False
            return False

        cap = cv2.VideoCapture(self._rtsp_url)
        ok, frame = cap.read()
        cap.release()

        if not ok or frame is None:
            self._logger.log(f"[Cam{self._num}] ERROR: No se pudo capturar imagen.")
            self.res = False
            return

        # Carpeta y ruta
        carpeta = os.path.join(capture_dir, str(fecha_hora.year), f"{fecha_hora.month:02}", f"{fecha_hora.day:02}", str(pin))
        os.makedirs(carpeta, exist_ok=True)
        self._ruta = os.path.join(carpeta, f"c{self._num}_{pin}.jpg")

        #guardar imagen
        cv2.imwrite(self._ruta, frame)
        self._logger.log(f"[Cam{self._num}] Guardada imagen en: {self._ruta}")
        self.res = True
