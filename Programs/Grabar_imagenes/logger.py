import os
import datetime
import threading
from settings import LOG_DIR

class Logger:
    def __init__(self, base_dir=None):
        self._base_dir = base_dir or LOG_DIR
        os.makedirs(self._base_dir, exist_ok=True)
        self._lock = threading.Lock()

    def log(self, mensaje, console=True):
        fecha = datetime.datetime.now()
        fecha_str = fecha.strftime("%Y-%m-%d")
        timestamp = fecha.strftime("%Y-%m-%d %H:%M:%S:%f")

        # Estructura de carpetas año/mes/día
        log_folder = os.path.join(self._base_dir, str(fecha.year), f"{fecha.month:02}", f"{fecha.day:02}")
        os.makedirs(log_folder, exist_ok=True)

        # se crea un fichero log para grabar imágenes
        log_file = os.path.join(log_folder, f"grabar_imagenes_log_{fecha_str}.txt")
        linea = f"{timestamp} - {mensaje}"

        with self._lock:            # Condición de carrera: protección para evitar que varios hilos escriban a la vez en el log o en la consola
            if console:
                print(linea)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(linea + "\n")


