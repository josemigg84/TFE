import os
import glob
import time
import stat


class QueueManager:
    def __init__(self, queue_dir, logger=None):
        self.queue_dir = queue_dir      # directorio de la cola FIFO
        self.logger = logger            # logger
        os.makedirs(queue_dir, exist_ok=True)       # si no existe el directorio de la cola, lo crea

    # Quitar solo lectura en Windows
    def _quitar_solo_lectura(self, path):
        try:
            os.chmod(path, stat.S_IWRITE | stat.S_IWUSR)
        except Exception:
            pass

    # metodo para eliminar ficheros de la cola. Con varios reintentos e intento de renombrar el fichero antes de borrarlo
    def remove(self, path, intentos=5, espera=0.2):
        if not os.path.exists(path):
            return True

        nombre = path
        for intento in range(1, intentos + 1):
            try:
                self._quitar_solo_lectura(nombre)
                os.remove(nombre)
                if self.logger:
                    self.logger.log(f"Archivo eliminado: {path}")
                return True
            except PermissionError:
                # Intento de renombrar fichero por fallo de permiso y borrarlo en la siguiente iteración
                try:
                    base = os.path.basename(nombre)
                    tmp = os.path.join(os.path.dirname(nombre), f"{base}_borrar{intento}")
                    os.replace(nombre, tmp)  # renombra dentro de la misma carpeta
                    nombre = tmp
                except Exception:
                    pass
                time.sleep(espera)
            except FileNotFoundError:
                return True
            except OSError:
                time.sleep(espera)

        # Si no se ha conseguido borrar, se llega aquí
        if self.logger:
            self.logger.log(f"No se pudo eliminar tras {intentos} reintentos: {path}")
        return False

    # obtener el siguiente fichero de la cola FIFO
    def get_next(self):
        archivos = sorted(glob.glob(os.path.join(self.queue_dir, "*.json")), key=os.path.getctime)  # primero ordenar por fecha
        return archivos[0] if archivos else None        # devuelve el más antiguo, o None si no hay

    # contar cuantos ficheros hay en la cola FIFO
    def count(self):
        files = glob.glob(os.path.join(self.queue_dir, "*.json"))
        return len(files)