import json
import os
import datetime
import settings
import shutil

class JsonFichero:
    def __init__(self, path, logger):
        self.logger = logger
        self.db_id = 0
        self.pin = ""
        self.skid: str = ""
        self.modelo_ext = 0
        self.modelo = 0
        self.cam1 = False
        self.cam2 = False
        self.path_in = path
        self.path_base = ""
        self.datetime_aplicacion = ""
        self.datetime_grabacion = ""
        self.path_img_cam1 = ""
        self.path_img_cam2 = ""
        self.res_cam1 = None
        self.res_cam2 = None

    # Metodo leer del fichero Json
    def leer(self):
        with open(self.path_in, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.db_id = int(data["db_id"])             # id
        self.pin = str(data["pin"])                 #número de carrocería
        self.skid = str(data["skid"])                  # skid
        self.modelo_ext = int(data["modelo"])          # modelo externo (PLC)
        self.modelo = settings.MODELOS[self.modelo_ext]     # modelo interno del programa
        self.path_base = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), str(data["path"])) #la ruta actual
        self.datetime_aplicacion = data["datetime_aplicacion"] # fecha de aplación
        self.datetime_grabacion = data["datetime_grabacion"]    #fecha de grabacion
        self.cam1 = bool(data["cam1"])          # cam1 activa
        self.cam2 = bool(data["cam2"])          # cam2 activa

        if self.cam1:
            self.path_img_cam1 = os.path.join(self.path_base, f'c1_{data["pin"]}.jpg')      # construir el path de la imagen de la cámara 1
        if self.cam2:
            self.path_img_cam2 = os.path.join(self.path_base, f'c2_{data["pin"]}.jpg')      # construir el path de la imagen de la cámara 2

        # validaciones
        if not self.cam1 and not self.cam2:
            raise ValueError(f"JSON inválido: ninguna cámara activa (cam1/cam2). Fichero: {self.path_in}")
        if self.modelo not in (1, 2):
            raise ValueError(f"JSON inválido: modelo no configurado; recibido {self.modelo_ext!r}")

        self.logger.log(f"JSON leído OK: {self.path_in}")
        self.logger.log(f"Analizar CAM 1: {self.cam1}")
        self.logger.log(f"Analizar CAM 2: {self.cam2}")
        self.logger.log(f"Path img CAM 1: {self.path_img_cam1}")
        self.logger.log(f"Path img CAM 2: {self.path_img_cam2}")
        self.logger.log(f"ID: {self.db_id} ")
        self.logger.log(f"PIN carrocería: {self.pin}")
        self.logger.log(f"SKID de carrocería: {self.skid}")
        self.logger.log(f"Modelo externo: {self.modelo_ext}")
        self.logger.log(f"Modelo interno: {self.modelo}")
        self.logger.log(f"Fecha de aplicación: {self.datetime_aplicacion}")
        self.logger.log(f"Fecha de grabación: {self.datetime_grabacion}")

        if settings.COPIA_JSON_IN_OUT:
            path_guardar_json_in =  os.path.join(self.path_base, f'{self.pin}_in.json')
            os.makedirs(os.path.dirname(path_guardar_json_in), exist_ok=True)
            if not os.path.exists(path_guardar_json_in):
                shutil.copy(self.path_in, path_guardar_json_in)
                self.logger.log(f"JSON de entrada copiado a: {path_guardar_json_in}")
            else:
                self.logger.log(f"JSON de entrada no copiado en: {path_guardar_json_in} porque ya existe")


    # Metodo guardar fichero Json con el resultado
    def escribir(self):

        if self.res_cam1 is None or self.res_cam2 is None:
            raise ValueError("Faltan resultados en res_cam1 o res_cam2")    #elevar excepción para que la trate el main.py

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fecha_aplicacion = self.datetime_aplicacion or now
        fecha_analisis = now

        # Selección de rangos según modelo
        if self.modelo == 1:
            base1, base2 = 1, 4   # para el id_elemento en la BBDD
        elif self.modelo == 2:
            base1, base2 = 7, 11   # para el id_elemento en la BBDD
        else:
            raise ValueError(f"Modelo interno inválido: {self.modelo}")

        resultados = []
        # Procesar res_cam1
        for i, cordon in enumerate(self.res_cam1["por_cordon"]):
            segs = [
                {"inicio": round(ini, 6), "fin": round(fin, 6)}
                for ini, fin in cordon["segmentos"]
            ]
            resultados.append({
                "id_elemento": base1 + i,
                "resultado": len(segs) == 0,
                "segmentos": segs
            })

        # Procesar res_cam2
        for i, cordon in enumerate(self.res_cam2["por_cordon"]):
            segs = [
                {"inicio": round(ini, 6), "fin": round(fin, 6)}
                for ini, fin in cordon["segmentos"]
            ]
            resultados.append({
                "id_elemento": base2 + i,
                "resultado": len(segs) == 0,
                "segmentos": segs
            })
        # Construir el diccionario final para escribirlo en el JSON
        data_out = {
            "id_carroceria": self.db_id,
            "modelo": f"{self.modelo_ext}",
            "pin": self.pin,
            "skid": self.skid,
            "fecha_aplicacion": fecha_aplicacion,
            "analisis": {
                "fecha_hora": fecha_analisis,
                "resultados": resultados
            }
        }
        # Asegurar carpeta y guardar JSON
        path_destino = os.path.join(settings.PATH_GUARDAR_JSON, f"{self.pin}_out.json")
        os.makedirs(os.path.dirname(path_destino), exist_ok=True)
        with open(path_destino, "w", encoding="utf-8") as f:               #si hay otro fichero igual -> abre para escritura y reemplaza el contenido.
            json.dump(data_out, f, indent=2, ensure_ascii=False)
        self.logger.log(f"JSON guardado en: {path_destino}")

        if settings.COPIA_JSON_IN_OUT:
            path_guardar_json_out = os.path.join(self.path_base, f'{self.pin}_out.json')
            os.makedirs(os.path.dirname(path_guardar_json_out), exist_ok=True)
            if not os.path.exists(path_guardar_json_out):
                with open(path_guardar_json_out, "w", encoding="utf-8") as f:       #si hay otro fichero igual -> abre para escritura y reemplaza el contenido.
                    json.dump(data_out, f, indent=2, ensure_ascii=False)
                self.logger.log(f"JSON de salida copiado a: {path_guardar_json_out}")
            else:
                self.logger.log(f"JSON de salida no copiado en: {path_guardar_json_out} porque ya existe")