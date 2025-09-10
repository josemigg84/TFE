import os
import datetime
from settings import LOG_DIR

class Logger:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or LOG_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def log(self, mensaje, console=True):
        fecha = datetime.datetime.now()
        fecha_str = fecha.strftime("%Y-%m-%d")
        timestamp = fecha.strftime("%Y-%m-%d %H:%M:%S:%f")

        # Estructura de carpetas año/mes/día
        log_folder = os.path.join(self.base_dir, str(fecha.year), f"{fecha.month:02}", f"{fecha.day:02}")
        os.makedirs(log_folder, exist_ok=True)

        log_file = os.path.join(log_folder, f"analizador_log_{fecha_str}.txt") # crear fichero log de analizador
        linea = f"{timestamp} - {mensaje}"

        if console:
            print(linea)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
