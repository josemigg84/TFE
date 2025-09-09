import json
import os


class JsonFichero:
    def __init__(self, db_id, pin, skid, modelo, path, datetime_aplicacion, datetime_grabacion, path_salida, logger):
        self._logger = logger
        self._db_id = db_id
        self._pin = pin
        self._skid = skid
        self._modelo = modelo
        self._cam1 = True
        self._cam2 = True
        self._path = path
        self._datetime_aplicacion = datetime_aplicacion
        self._datetime_grabacion = datetime_grabacion
        self._path_salida = path_salida

    # Metodo que guarda el fichero Json con los datos de las capturas y la info de la carrocería
    def escribir(self):

        path = self._path.replace('\\', '/')

        # Construir el diccionario de salida
        data_out = {
            "db_id": self._db_id,       # identificador
            "pin": self._pin,           # número de carrocería
            "skid": self._skid,         # número de skid
            "modelo": self._modelo,     # modelo
            "cam1": self._cam1,         # == True si se usa la cámara 1
            "cam2": self._cam2,         # == True si se usa la cámara 2
            "path": path,               # ruta
            "datetime_aplicacion": self._datetime_aplicacion,   # fecha de aplicación de masilla
            "datetime_grabacion": self._datetime_grabacion      # fecha de grabación de la imagen
        }

        # Asegurar carpeta y guardar JSON

        os.makedirs(os.path.dirname(self._path_salida), exist_ok=True)
        with open(self._path_salida, "w", encoding="utf-8") as f:               #si hay otro fichero igual -> abre para escritura y reemplaza el contenido.
            json.dump(data_out, f, indent=2, ensure_ascii=False)
        self._logger.log(f"JSON guardado en: {self._path_salida}")
