import os
import cv2
import settings

debug_counter = 1

class Imagen:
    def __init__(self, path, logger):
        self.logger = logger
        self.path = path       # se guarda la ruta de la imagen original (está protegida la ruta para no poder sobreescribir la imagen de entrada)
        self.imagenPath = cv2.imread(path)  # Guardar imagen original sin tocar, para volver a punto inicial. Necesario para algún analisis
        if self.imagenPath is None:
            self.logger.log(f"Fallo al cargar la imagen desde: {path}")
            raise ValueError(f"Fallo al cargar la imagen desde: {path}")
        self.original = self.imagenPath.copy()    # En la imagen original se van haciendo las transformaciones definitivas para ir añadiendo inf al resultado
        self.actual = self.imagenPath.copy()      # En la imagen actual se van haciendo las transformaciones intermedias. También se pueden guardar mediante: guardar_debug

    # convertir a escala de grises
    def gris(self):
        self.actual = cv2.cvtColor(self.actual, cv2.COLOR_BGR2GRAY)
        return self

    # suavizar imagen con filtro de la mediana
    def suavizar(self, k=5):    # si no se pone nada, por defecto kernel = 5
        self.actual = cv2.medianBlur(self.actual, k)
        return self

    # ecualizar el histograma
    def ecualizar(self):
        self.actual = cv2.equalizeHist(self.actual)
        return self

    # binarizar la imagen con un umbral
    def binarizar(self, umbral=80):  # si no se pone nada, por defecto UMBRAL = 80
        _, self.actual = cv2.threshold(self.actual, umbral, 255, cv2.THRESH_BINARY)
        return self

    # guardar imagen en ruta de salida
    def guardar(self, ruta_salida, usar_original=False): #evita sobreescribir sobre el archivo original
        img = self.original if usar_original else self.actual
        ruta_salida_abs = os.path.abspath(ruta_salida)
        path_original_abs = os.path.abspath(self.path)

        if ruta_salida_abs == path_original_abs:
            self.logger.log("No se puede sobrescribir la imagen original")
            raise ValueError("No se puede sobrescribir la imagen original")

        cv2.imwrite(ruta_salida, img)
        return self

    # resetear la imagen, normalmente para la imagen original
    def reset(self):
        self.actual = self.imagenPath.copy()
        return self

    # guardar imagen en carpeta debug
    def guardar_debug(self, path_debug, nombre, usar_original=False):
        global debug_counter
        img = self.original if usar_original else self.actual       # qué imagen guardar
        ruta = os.path.join(os.path.dirname(path_debug), "debug")   #calcular la ruta
        os.makedirs(ruta, exist_ok=True)        #si no existe la ruta, se crea
        path = os.path.join(ruta, f"{debug_counter}_{nombre}.{settings.FORMATO_GUARDAR_DEBUG}") #calcular el path
        cv2.imwrite(path, img)      # guardar la imagen
        self.logger.log(f"Imagen de debug guardada en: {path_debug}")
        debug_counter += 1          # aumentar el contador
        return self


