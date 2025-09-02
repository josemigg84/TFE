import os
import cv2
import math
import datetime
import numpy as np
import settings
import tensorflow as tf
import time
from abc import ABC, abstractmethod
import imagen


class AnalizadorCordonesBase(ABC):

    @abstractmethod
    def localizar(self):
        pass            # la clase hija debe implementar este metodo

    @abstractmethod
    def modificar(self):
        pass            # la clase hija debe implementar este metodo

    @abstractmethod
    def analizar(self):
        pass            # la clase hija debe implementar este metodo

    @abstractmethod
    def finalizar(self):
        pass            # la clase hija debe implementar este metodo

    #metodo abstracto que se implementa en la clase hija y que por polimorfismo llama a _buscar_angulo_vertical o _buscar_angulo_horizontal
    @abstractmethod
    def _buscar_angulo(self, roi1, roi2, roi_x1, roi_y1, roi_x2, roi_y2, roi_w, roi_h, umbral_res):
        pass

    def __init__(self, config, path_img, logger, fichero):
        self.config = config
        self.path_img = path_img
        self.path_debug = path_img
        self.logger = logger
        self.fichero = fichero
        self.imagen = imagen.Imagen(path_img, self.logger)  # tiene la imagen original y la actual
        self.cordones = list(self.config["cordones"].values())

    #metodo para calcular la posicion de la carroceria según la localizacion de un patron
    def _posicion(self, roi, pos_ini, img_patron, umbral_bin = settings.UMBRAL_BIN_POSICION, umbral_res = settings.UMBRAL_RES_POSICION, suavizar=True, suavizar_kernel=5):    #no ha se ha definido como abstracto porque es el mismo metodo para todas las clases
        self.logger.log("Inicio de posicionamiento")

        roi_x, roi_y, roi_w, roi_h = roi   # definir roi:  x e y del punto superior izquierdo, ancho y alto

        # volver a cargar en la imagen actual la imagen original, modificar imagenes y guardar en debug
        self.imagen.reset()
        # modificar imagenes y guardar en debug
        if suavizar:
            if settings.IMAGEN_DEBUG:
                self.imagen.guardar_debug(self.path_debug, "original")
                self.imagen = self.imagen.gris().guardar_debug(self.path_debug, "Pos_gris").suavizar(suavizar_kernel).guardar_debug(self.path_debug, "Pos_suavizada").ecualizar().guardar_debug(self.path_debug, "Pos_ecualizada").binarizar(umbral_bin).guardar_debug(self.path_debug, "Pos_binaria")
                img_patron = img_patron.gris().guardar_debug(self.path_debug, "Pos_patron")
            else:
                self.imagen = self.imagen.gris().suavizar(suavizar_kernel).ecualizar().binarizar(umbral_bin)
                img_patron = img_patron.gris()
        else:
            if settings.IMAGEN_DEBUG:
                self.imagen.guardar_debug(self.path_debug, "original")
                self.imagen = self.imagen.gris().guardar_debug(self.path_debug, "Pos_gris").ecualizar().guardar_debug(self.path_debug, "Pos_ecualizada").binarizar(umbral_bin).guardar_debug(self.path_debug, "Pos_binaria")
                img_patron = img_patron.gris().guardar_debug(self.path_debug, "Pos_patron")
            else:
                self.imagen = self.imagen.gris().ecualizar().binarizar(umbral_bin)
                img_patron = img_patron.gris()

        # Dibujar la ventana de búsqueda (ROI) en la imagen
        cv2.rectangle(self.imagen.original, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), settings.COLOR_VENTANA, thickness=1)

        # Obtener las dimensiones del patrón
        alto_patron, ancho_patron = img_patron.actual.shape

        # Extraer la ROI de la imagen binaria, imagen[desde_fila:hasta_fila, desde_columna:hasta_columna]
        roi = self.imagen.actual[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]

        # Coincidencia de plantillas para buscar el patrón en la roi
        resultado = cv2.matchTemplate(roi, img_patron.actual, cv2.TM_CCOEFF_NORMED)

        # Encontrar la ubicación del mejor ajuste (mayor coincidencia)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultado)

        if max_val >= umbral_res:            # Comprobar si la coincidencia máxima supera el umbral
            color_linea = settings.COLOR_VERDE
            res_pos = True
        else:
            color_linea = settings.COLOR_ROJO
            res_pos = False

        # max_loc contiene la ubicación (x, y) del punto superior izquierdo de la mejor coincidencia
        pat_x, pat_y = max_loc
        punto_superior_izquierdo = (roi_x + pat_x, roi_y + pat_y)
        punto_inferior_derecho = (punto_superior_izquierdo[0] + ancho_patron, punto_superior_izquierdo[1] + alto_patron)

        # Dibujar un rectángulo alrededor de la mejor coincidencia
        cv2.rectangle(self.imagen.original, punto_superior_izquierdo, punto_inferior_derecho, color_linea, thickness=1)

        # Calcular el centro del patrón
        centro_x = punto_superior_izquierdo[0] + ancho_patron // 2
        centro_y = punto_superior_izquierdo[1] + alto_patron // 2

        # Dibujar una cruz en el centro del patrón
        longitud_cruz = 10
        cv2.line(self.imagen.original, (centro_x - longitud_cruz, centro_y), (centro_x + longitud_cruz, centro_y), color_linea, thickness=1)
        cv2.line(self.imagen.original, (centro_x, centro_y - longitud_cruz), (centro_x, centro_y + longitud_cruz), color_linea, thickness=1)

        # Escribir el porcentaje de coincidencia y coordenadas
        porcentaje_coincidencia = max_val * 100
        texto = f"{porcentaje_coincidencia:.2f}% ({centro_x},{centro_y})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(self.imagen.original, texto, (punto_superior_izquierdo[0] - 35, punto_superior_izquierdo[1] + alto_patron + 30), font, 0.5, color_linea, thickness=1, lineType=cv2.LINE_AA)
        self.logger.log(f"Coincidencia del patrón: {porcentaje_coincidencia} %")

        if settings.IMAGEN_DEBUG:
            self.imagen = self.imagen.guardar_debug(self.path_debug, "Pos_salida", usar_original=True)

        res_pos_centro = (centro_x, centro_y)
        res_pos_dif_centro = (centro_x - pos_ini[0], centro_y - pos_ini[1])

        self.logger.log(f"Posición patrón, centro localizado en: {res_pos_centro}")
        self.logger.log(f"Diferencia centro: {res_pos_dif_centro}")
        self.logger.log(f"RESULTADO posicionamiento: {res_pos}")

        return res_pos_centro, res_pos_dif_centro, res_pos, porcentaje_coincidencia

    #metodo para calcular el ángulo de la imagen según la lozalización de una ventana de la carroceria
    def _angulo(self, roi, dif_centro, umbral_bin = settings.UMBRAL_BIN_ANGULO, umbral_res = settings.UMBRAL_RES_ANGULO):
        self.logger.log("Inicio de busqueda de ángulo")

        # definir la región de interés pasada como argumento, x e y de los puntos de inicio de la roi, ancho y alto
        roi_x1_aux, roi_y1_aux, roi_x2_aux, roi_y2_aux, roi_w, roi_h = roi

        # recalcular las roi según el resultado del metodo posicion
        roi_x1 = roi_x1_aux + dif_centro[0]
        roi_y1 = roi_y1_aux + dif_centro[1]
        roi_x2 = roi_x2_aux + dif_centro[0]
        roi_y2 = roi_y2_aux + dif_centro[1]

        # volver a cargar en la imagen actual la imagen original, modificar imagenes y guardar en debug
        self.imagen.reset()
        if settings.IMAGEN_DEBUG:
            self.imagen = (
                self.imagen
                .gris().guardar_debug(self.path_debug, "Ang_gris")
                .suavizar().guardar_debug(self.path_debug, "Ang_suavizada")
                .ecualizar().guardar_debug(self.path_debug, "Ang_ecualizada")
                .binarizar(umbral_bin).guardar_debug(self.path_debug, "Ang_binaria")
            )
        else:
            self.imagen = self.imagen.gris().suavizar().ecualizar().binarizar(umbral_bin)
        # ROI: imagen_binaria[desde_fila:hasta_fila, desde_columna:hasta_columna]
        roi1 = self.imagen.actual[roi_y1:roi_y1 + roi_h, roi_x1:roi_x1 + roi_w]
        roi2 = self.imagen.actual[roi_y2:roi_y2 + roi_h, roi_x2:roi_x2 + roi_w]

        angulo_resultado, angulo_dif, angulo_res = self._buscar_angulo(roi1, roi2, roi_x1, roi_y1, roi_x2, roi_y2, roi_w, roi_h, umbral_res)
        if settings.IMAGEN_DEBUG:
            self.imagen = self.imagen.guardar_debug(self.path_debug, "Ang_salida", usar_original=True)

        return angulo_resultado, angulo_dif, angulo_res

    #metodo para buscar el angulo vertical en el patrón binarizado
    def _buscar_angulo_vertical(self, roi1, roi2, roi_x1, roi_y1, roi_x2, roi_y2, roi_w, roi_h, umbral_res):
        # Busca ángulos verticales, localizando puntos e iterando sobre una línea horizontal para buscar el primer pixel negro en la imagen binarizada
        self.logger.log("Inicio de busqueda de ángulo vertical")
        x1, y1, x2, y2, dx, dy = 0,0,0,0,0,0
        res1 = False  # resultado parcial de la roi1
        res2 = False  # resultado parcial de la roi2
        # .shape[0] → número de filas, .shape[1] → número de columnas, .shape[2] → número de canales de color
        # Buscar el primer píxel negro (valor 0) en la roi 1
        for x_rel in range(roi1.shape[1]):
            if roi1[0, x_rel] == 0:
                x1 = roi_x1 + x_rel
                y1 = roi_y1
                res1 = True
                break
            # Buscar el primer píxel negro (valor 0) en la roi 2
        for x_rel in range(roi2.shape[1]):
            if roi2[0, x_rel] == 0:
                x2 = roi_x2 + x_rel
                y2 = roi_y2
                res2 = True
                break
        # Diferencias
        dx = x2 - x1
        dy = y2 - y1
        # Ángulo respecto al eje vertical
        angulo_rad = math.atan2(dy, dx)
        angulo_deg = math.degrees(angulo_rad)
        angulo_resultado = 90 - abs(angulo_deg)

        # Texto del ángulo
        texto = f"Angulo: {angulo_resultado:.4f}"
        font = cv2.FONT_HERSHEY_SIMPLEX

        if abs(angulo_resultado - self.config['cfg_ini']['ANGULO_INI']) <= umbral_res:
            color_linea = settings.COLOR_VERDE
        else:
            color_linea = settings.COLOR_ROJO
        #modifica la imagen original con el texto del resultado y dibujando las líneas calculadas
        cv2.putText(self.imagen.original, texto, (roi_x1 + 5, roi_y1 - 10), font, 0.5, color_linea, thickness=1, lineType=cv2.LINE_AA)
        cv2.line(self.imagen.original, (x1, y1), (x2, y2), settings.COLOR_MORADO, thickness=1)
        cv2.line(self.imagen.original, (x2, y1), (x2, y2), settings.COLOR_MORADO, thickness=1)
        cv2.line(self.imagen.original, (roi_x1, roi_y1), (roi_x1 + roi_w, roi_y1), settings.COLOR_MORADO, thickness=1)
        cv2.line(self.imagen.original, (roi_x2, roi_y2), (roi_x2 + roi_w, roi_y2), settings.COLOR_MORADO, thickness=1)

        #puntos resultantes
        p1 = (x1, y1)
        p2 = (x2, y2)

        #Guardar resultados
        angulo_dif = angulo_resultado - self.config['cfg_ini']['ANGULO_INI']
        angulo_res = res1 and res2 and (abs(angulo_resultado - self.config['cfg_ini']['ANGULO_INI']) <= umbral_res)

        #Log de resultados
        self.logger.log(f"Calculo ángulo, localizado punto 1 en: {p1}")
        self.logger.log(f"Calculo ángulo, localizado punto 2 en: {p2}")
        self.logger.log(f"Calculo ángulo resultante: {angulo_resultado}")
        self.logger.log(f"Diferencia ángulo: {angulo_dif}")
        self.logger.log(f"RESULTADO ángulo: {angulo_res}")

        return angulo_resultado, angulo_dif, angulo_res

    #metodo para buscar el angulo horizontal en el patrón binarizado
    def _buscar_angulo_horizontal(self, roi1, roi2, roi_x1, roi_y1, roi_x2, roi_y2, roi_w, roi_h, umbral_res):
        # Busca ángulos horizontales, localizando puntos e iterando sobre una línea vertical para buscar el primer pixel blanco en la imagen binarizada
        self.logger.log("Inicio de busqueda de ángulo horizontal")

        (x1, y1, x2, y2) = (0,0,0,0)
        res1 = False  # resultado parcial de la roi1
        res2 = False  # resultado parcial de la roi2
        # .shape[0] → número de filas, .shape[1] → número de columnas, .shape[2] → número de canales de color
        # Buscar el primer píxel blanco (valor 255) en la roi 1
        for y_rel in range(roi1.shape[0]):
            if roi1[y_rel, 0] == 255:
                x1 = roi_x1
                y1 = roi_y1 + y_rel
                res1 = True
                break
            # Buscar el primer píxel blanco (valor 255) en la roi 2
        for y_rel in range(roi2.shape[0]):
            if roi2[y_rel, 0] == 255:
                x2 = roi_x2
                y2 = roi_y2 + y_rel
                res2 = True
                break
        # Diferencias
        dx = x2 - x1
        dy = y1 - y2

        # Ángulo respecto al eje horizontal
        angulo_rad = math.atan2(dy, dx)
        angulo_deg = math.degrees(angulo_rad)
        angulo_resultado = angulo_deg

        # Texto del ángulo
        texto = f"Angulo: {angulo_resultado:.4f}"
        font = cv2.FONT_HERSHEY_SIMPLEX

        if abs(angulo_resultado - self.config['cfg_ini']['ANGULO_INI']) <= umbral_res:
            color_linea = settings.COLOR_VERDE
        else:
            color_linea = settings.COLOR_ROJO
        #modifica la imagen original con el texto del resultado y dibujando las líneas calculadas
        cv2.putText(self.imagen.original, texto, (roi_x1 + 5, roi_y1 - 10), font, 0.5, color_linea, thickness=1, lineType=cv2.LINE_AA)
        cv2.line(self.imagen.original, (x1, y1), (x2, y2), settings.COLOR_MORADO, thickness=1)
        cv2.line(self.imagen.original, (x1, y1), (x2, y1), settings.COLOR_MORADO, thickness=1)
        cv2.line(self.imagen.original, (roi_x1, roi_y1), (roi_x1, roi_y1 + roi_h), settings.COLOR_MORADO, thickness=1)
        cv2.line(self.imagen.original, (roi_x2, roi_y2), (roi_x2, roi_y2 + roi_h), settings.COLOR_MORADO, thickness=1)

        # puntos resultantes
        p1 = (x1, y1)
        p2 = (x2, y2)

        # Guardar resultados
        angulo_dif = angulo_resultado - self.config['cfg_ini']['ANGULO_INI']
        angulo_res = res1 and res2 and (abs(angulo_resultado - self.config['cfg_ini']['ANGULO_INI']) <= umbral_res)

        # Log de resultados
        self.logger.log(f"Calculo ángulo, localizado punto 1 en: {p1}")
        self.logger.log(f"Calculo ángulo, localizado punto 2 en: {p2}")
        self.logger.log(f"Calculo ángulo resultante: {angulo_resultado}")
        self.logger.log(f"Diferencia ángulo: {angulo_dif}")
        self.logger.log(f"RESULTADO ángulo: {angulo_res}")

        return angulo_resultado, angulo_dif, angulo_res

    #metodo para calcular la matriz de traslación + rotación según los calculos anteriores
    def _matriz(self, centro, dif_centro, angulo):
        self.logger.log("Inicio de cálculo de matriz traslación-rotación")
        dif_x, dif_y = dif_centro
        angulo_rad = math.radians(angulo)
        # Matriz de rotación (2x3)
        matriz_rot = cv2.getRotationMatrix2D(center=centro, angle=angulo_rad, scale=1.0)
        # Agregar la traslación
        matriz_rot[0, 2] += dif_x
        matriz_rot[1, 2] += dif_y
        self.logger.log("Se ha calculado una matriz de traslación-Rotación")
        return matriz_rot

    # Función para dibujar los cordones en la imagen
    def _dibujar_cordones(self, cordones, color, grosor, nombre="Cordones"):
        # Dibujar líneas conectando los puntos en la lista para cada cordon
        self.logger.log("Dibujo en imagen de cordones ")
        for cordon in cordones:
            for i in range(len(cordon) - 1):
                cv2.line(self.imagen.original, cordon[i], cordon[i + 1], color, grosor)
        if settings.IMAGEN_DEBUG:
            self.imagen = self.imagen.guardar_debug(self.path_debug, nombre, usar_original=True)

    #Metodo para dibujar las ventanas de recorte para la FCN U-Net
    def _dibujar_ventanas_recortes_analisis(self):
        # Dibujar las ventanas del análisis
        self.logger.log("Dibujo en imagen de ventanas de recorte para analisis")
        if settings.DIBUJAR_VENTANAS_RECORTE:  # se puede elegir en settings.py si imprimir o no
            ancho_ventana, alto_ventana = settings.TAMANO_RECORTE
            for (x, y) in self.config["puntos_recortes_analisis"]:
                cv2.rectangle(self.imagen.original, (x, y), (x + ancho_ventana, y + alto_ventana), color=settings.COLOR_AZUL, thickness=1)
        if settings.IMAGEN_DEBUG:
            self.imagen = self.imagen.guardar_debug(self.path_debug, "Ventanas_recortes", usar_original=True)

    # Metodo que realiza el analisis de masilla con una FCN U-Net
    def _analizar_modelo(self, cordones_modificados):
        self.logger.log("Inicio de análisis de modelo")
        # análisis del modelo U-Net
        start = time.time()             #inicio de medición del tiempo de análisis

        # Cargar modelo U-Net entrenado previamente
        model = tf.keras.models.load_model(settings.MODEL_PATH)

        self.imagen.reset()  #resetear la imagen actual
        altura, anchura = self.imagen.actual.shape[:2]
        imagen_masilla = np.full((altura, anchura, 3), 255, dtype=np.uint8) # crear imagen para máscara, con píxeles blancos

        # Preparar lote (batch), todos los recortes de la imagen se pasan en un solo lote
        ventanas_validas = []
        coords_validas = []

        for i, (x, y) in enumerate(self.config["puntos_recortes_analisis"]):
            ventana = self.imagen.actual[y:y + 256, x:x + 256]
            if ventana.shape != (256, 256, 3):
                self.logger.log(f"Ventana {i} fuera de límites: no se analiza.")
                continue
            ventanas_validas.append(ventana / 255.0)
            coords_validas.append((x, y))

        # Convertir batch y predecir
        batch = np.array(ventanas_validas, dtype=np.float32)        # convertir en array de numpy con tipo float32
        preds = model.predict(batch, verbose=0)             # se pasa al modelo el lote al modelo entrenado y devuelve las predicciones

        end = time.time()           #fin del tiempo medido del análisis
        self.logger.log(f"Análisis finalizado: tiempo: {end - start:.4f} segundos")    #el tiempo se escribe en el log

        # Aplicar máscaras de la predicción a la imagen resultante (blanca)
        for i, pred in enumerate(preds):                # Cada pred es un tensor con forma (256, 256, 1). Corresponde con una ventana de recorte de 256x256 píxeles.
            x, y = coords_validas[i]                    # Cada posición (x, y) contiene un valor de probabilidad entre 0 y 1.  -> ej: pred = [ [0.02], [0.6], [0.75], ... , [0.99]]
            mascara = (pred > 0.5).astype(np.uint8).squeeze()       # valores de predicción por encima de 0.5 (50%) son masilla, el resto fondo, squeeze() quita la ultima dimension dejando 256x256, máscara es una matriz binaria con 1 (masilla) y 0 (fondo) para cada recorte
            region = imagen_masilla[y:y + 256, x:x + 256]           # region es la posición (según el recorte de la imagen inicial) localizada en la imagen blanca creada antes
            region[mascara == 1] = [0, 0, 0]                        # se pintan de negro los píxeles de masilla que pertenecen a ese recorte en la imagen blanca
        imagen_mascara = imagen_masilla.copy()

        if settings.IMAGEN_DEBUG:  # no se llama a dibujar cordones ni al metodo imagen.guardar_debug porque np.ndarray no es de la clase Imagen
            ruta = os.path.join(os.path.dirname(self.path_debug), "debug")
            os.makedirs(ruta, exist_ok=True)
            path_debug = os.path.join(ruta, f"{imagen.debug_counter}_mascara_masilla.{settings.FORMATO_GUARDAR_MASK}")
            cv2.imwrite(path_debug, imagen_masilla)
            self.logger.log(f"Imagen de debug guardada en: {path_debug}")
            imagen.debug_counter += 1

        for cordon in cordones_modificados:
            for i in range(len(cordon) - 1):
                cv2.line(imagen_masilla, cordon[i], cordon[i + 1], settings.COLOR_MORADO, 1)

        if settings.IMAGEN_DEBUG:  # no se llama a dibujar cordones ni al metodo imagen.guardar_debug porque np.ndarray no es de la clase Imagen
            ruta = os.path.join(os.path.dirname(self.path_debug), "debug")
            os.makedirs(ruta, exist_ok=True)
            path_debug = os.path.join(ruta, f"{imagen.debug_counter}_mascara_masilla_cordones.{settings.FORMATO_GUARDAR_MASK}")
            cv2.imwrite(path_debug, imagen_masilla)
            self.logger.log(f"Imagen de debug guardada en: {path_debug}")
            imagen.debug_counter += 1
        if settings.IMAGEN_GUARDAR:
            path_res_mask = os.path.join(self.fichero.path_base, f"{self.__class__.__name__}_{self.fichero.pin}_mask.{settings.FORMATO_GUARDAR_MASK}")
            cv2.imwrite(path_res_mask, imagen_masilla)
            self.logger.log(f"Imagen CAM mask masilla, guardada en:: {path_res_mask}")

        return imagen_mascara

    #Función para calcular el resultado
    def _calcular_resultado(self, mascara, cordones):
        self.logger.log("Inicio de cálculo de resultados")

        # Cargar configuración desde settings
        margenes = self.config['cfg_ini']['MARGEN_PIXELES_CORDONES']
        limite_sin_masilla = self.config['segmentos']['limite_sin_masilla_matriz']
        min_malos_seguidos = self.config['segmentos']['min_malos_seguidos']
        min_buenos_seguidos = self.config['segmentos']['min_buenos_seguidos']
        redondeo = self.config['segmentos']['precision_decimales_normalizar']

        alto, ancho = mascara.shape[:2]   #alto y ancho de la máscara de entrada

        def _contar_sin_masilla(ymin, ymax, xmin, xmax):
            region = mascara[ymin:ymax, xmin:xmax]          #definir ventana
            pixeles_blancos = np.any(region != 0, axis=-1) if region.ndim == 3 else (region != 0)       # para cada pixel devuelve false si todos sus canales son 0, sino True
            return int(np.count_nonzero(pixeles_blancos))           #cuenta cuantos elementos distintos de 0 hay en el array, lo parsea a entero y lo devuelve

        # convertir márgenes en una lista de márgenes, uno para cada cordón
        if isinstance(margenes, (int, np.integer)):     #comprueba si margenes es de tipo entero
            marg_list = [int(margenes)] * len(cordones)
        else:
            marg_list = list(margenes)
            if len(marg_list) < len(cordones):
                marg_list += [marg_list[-1]] * (len(cordones) - len(marg_list))
            else:
                marg_list = marg_list[:len(cordones)]

        resultados = []
        total_malos = 0
        total_segmentos = 0
        total_malos_filtrados = 0

        for id_cordon, cordon in enumerate(cordones, start=1):  # empieza en 1
            margen = int(marg_list[id_cordon - 1])  # convierte a entero cada elemento (i-1)

            indicador_malos = []            # lista con valores 0, 1 según cada punto del cordón es bueno o malo, si tiene o no masilla
            for (x, y) in cordon:           # para cada punto del cordón se define una ventana cuadrada alrededor del tamaño del margen, que es la matriz
                xmin = max(0, x - margen)
                xmax = min(ancho, x + margen + 1)
                ymin = max(0, y - margen)
                ymax = min(alto, y + margen + 1)
                sin_masilla = _contar_sin_masilla(ymin, ymax, xmin, xmax)
                indicador_malos.append(1 if sin_masilla > limite_sin_masilla else 0)        # añade True o false para cada punto, dependiendo si tiene o no más fallos de masilla que el límite configurado

            num_malos = int(sum(indicador_malos))       # número de puntos malos por cordon
            total_malos += num_malos                    # total de puntos malos en todos los cordones
            # Extraer coordenadas exactas de los puntos malos
            puntos_malos_coords = [cordon[i] for i, res in enumerate(indicador_malos) if res == 1]      #list comprehension que construye la lista con las coordenadas de los puntos con fallo

            # segmentos de malos
            segmentos = []
            n = len(indicador_malos)
            i = 0

            while i < n:
                if indicador_malos[i] == 1:         # si el punto es malo busca hacia adelante
                    j = i
                    while j + 1 < n and indicador_malos[j + 1] == 1:
                        j += 1                       # avanza mientras encuentre puntos malos consecutivos
                    if (j - i + 1) >= min_malos_seguidos:       # si supera el limite configurado, se guarda como segmento malo
                        segmentos.append([i, j])                # se guarda el segmento [inicio, fin]
                    i = j + 1
                else:
                    i += 1                                      # si no era malo, avanza al siguiente punto

            # Si hay segmentos malos separados por < min_buenos_seguidos, se fusionan entre sí
            segmentos_fusionados = []
            for seg in segmentos:
                if len(segmentos_fusionados) == 0:     # si la lista está vacia y no hay segmentos fusionados
                    segmentos_fusionados.append(seg)        # en la primera iteración mete directamente el primer segmento
                else:
                    previo = segmentos_fusionados[-1]          # segmento previo
                    hueco = seg[0] - previo[1] - 1              # hueco entre segmentos, pixeles buenos
                    if hueco < min_buenos_seguidos:             # si están muy juntos
                        previo[1] = seg[1]                      # sobreescribe el índice final del segmento anterior para juntar los dos
                    else:
                        segmentos_fusionados.append(seg)        # no se fusionan y se guarda el segmento como estaba

            # calcula los puntos malos que pertenecen a segmentos ya filtrados, descartando el resto
            segmentos_filtrados = []
            for a, b in segmentos_fusionados:
                segmentos_filtrados.extend(range(a, b + 1))
            puntos_malos_coords_en_segmento = [cordon[i] for i in segmentos_filtrados if indicador_malos[i] == 1]
            num_malos_filtrados = len(puntos_malos_coords_en_segmento)
            total_malos_filtrados += num_malos_filtrados

            # normalizar segmentos por longitud del cordón (cada punto = 1 píxel porque el cordón está interpolado)
            m = len(cordon)  # nº de puntos del cordón

            segmentos_norm = []
            if m >= 2:
                total_len = m - 1  # distancia "total" en pasos de 1 píxel
                for a, b in segmentos_fusionados:
                    ini = round(a / total_len, redondeo)
                    fin = round(b / total_len, redondeo)
                    segmentos_norm.append((ini, fin))
            else:
                # si el cordón tiene menos de 2 puntos, no puede tener segmentos
                for _ in segmentos_fusionados:
                    segmentos_norm.append((0.0, 0.0))

            num_segmentos = len(segmentos_norm)
            total_segmentos += num_segmentos

            resultados.append({
                "cordon": id_cordon,  # empieza en 1
                "puntos_malos": num_malos,
                "puntos_malos_coords": puntos_malos_coords,
                "puntos_malos_coords_en_segmento": puntos_malos_coords_en_segmento,
                "puntos_malos_en_segmento": num_malos_filtrados,
                "segmentos": segmentos_norm,
            })
        salida = {
            "total_puntos_malos": total_malos,
            "total_puntos_malos_en_segmento": total_malos_filtrados,
            "total_segmentos": total_segmentos,
            "por_cordon": resultados
        }
        self.logger.log(f"Número de puntos sin masilla: {salida['total_puntos_malos']}")
        self.logger.log(f"Número de puntos sin masilla filtrados en segmentos: {salida['total_puntos_malos_en_segmento']}")
        self.logger.log(f"Número de segmentos sin masilla: {salida['total_segmentos']}")
        return salida

    # Metodo para finalizar y guardar resultado
    def _guardar_resultado(self, result):
        img_copy = self.imagen.original.copy()

        for num in range(1, len(result['por_cordon']) + 1):     # bucle que recorre la lista de diccionarios del resultado devuelto "por_cordon" en el metodo _calcular_resultado
            coords = next(c['puntos_malos_coords'] for c in result['por_cordon'] if c['cordon'] == num)    # en cada iteración del bucle obtiene la lista de coordenadas de los puntos malos de ese número de cordón
            for x, y in coords:                                                                            # para cada coordenada mala de lista calculada dibuja un círculo rojo
                cv2.circle(self.imagen.original, (x, y), 10, settings.COLOR_ROJO, thickness=-1)

        for num in range(1, len(result['por_cordon']) + 1):     # bucle que recorre la lista de diccionarios del resultado devuelto "por_cordon" en el metodo _calcular_resultado
            coords = next(c['puntos_malos_coords_en_segmento'] for c in result['por_cordon'] if c['cordon'] == num)    # en cada iteración del bucle obtiene la lista de coordenadas de los puntos malos filtrados ya en segmentos, de ese número de cordón
            for x, y in coords:                                                                           # para cada coordenada mala de lista calculada dibuja un círculo rojo
                cv2.circle(img_copy, (x, y), 10, settings.COLOR_ROJO, thickness=-1)

        if settings.IMAGEN_DEBUG:
            self.imagen = self.imagen.guardar_debug(self.path_debug, "fallos_puntos", usar_original=True)
            ruta = os.path.join(os.path.dirname(self.path_debug), "debug")
            os.makedirs(ruta, exist_ok=True)
            path_debug = os.path.join(ruta, f"{imagen.debug_counter}_fallos_segmentos.{settings.FORMATO_GUARDAR_DEBUG}")
            cv2.imwrite(path_debug, img_copy)
            self.logger.log(f"Imagen de debug guardada en: {path_debug}")
            imagen.debug_counter += 1

        # Escribir información del resultado en la imagen
        textos_info = [
            f"PIN:  {self.fichero.pin}",
            f"SKID:  {self.fichero.skid}",
            f"MODELO:  {self.fichero.modelo_ext} (interno: {self.fichero.modelo})",
            f"Aplicacion:  {self.fichero.datetime_aplicacion}",
            f"Analisis:  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Num. puntos en fallo (sin filtro):  {result['total_puntos_malos']}",
            f"Num. segmentos en fallo (con filtro):  {result['total_segmentos']}"
        ]

        # Se crean copias de las imagenes para superponerla
        fondo = self.imagen.original.copy()     #para la ventana de info en la imagen con puntos malos
        fondo2 = img_copy.copy()                #para la ventana de info en la imagen con segmentos malos

        alto_linea = 30
        ancho_texto = 490
        alto_total = alto_linea * len(textos_info) + 10

        # Dibujar rectángulos con fondo negro opaco
        cv2.rectangle(fondo, (5, 5), (5 + ancho_texto, 5 + alto_total), (0, 0, 0), -1)
        cv2.rectangle(fondo2, (5, 5), (5 + ancho_texto, 5 + alto_total), (0, 0, 0), -1)

        # Mezclar los rectángulos con la imagen original para simular semitransparencia
        alpha = 0.7  # 0 = transparente, 1 = opaco
        cv2.addWeighted(fondo, alpha, self.imagen.original, 1 - alpha, 0, self.imagen.original)
        cv2.addWeighted(fondo2, alpha, img_copy, 1 - alpha, 0, img_copy)

        # escribir los textos de información de la carrocería
        for i, texto in enumerate(textos_info):
            cv2.putText(self.imagen.original, texto, (10, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(img_copy, texto, (10, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv2.LINE_AA)

        #guardar imagenes en carpeta debug si está la opción activada
        if settings.IMAGEN_DEBUG:
            self.imagen = self.imagen.guardar_debug(self.path_debug, "fallos_puntos_info", usar_original=True)
            ruta = os.path.join(os.path.dirname(self.path_debug), "debug")
            os.makedirs(ruta, exist_ok=True)
            path_debug = os.path.join(ruta, f"{imagen.debug_counter}_fallos_segmentos_info.{settings.FORMATO_GUARDAR_DEBUG}")
            cv2.imwrite(path_debug, img_copy)
            self.logger.log(f"Imagen de debug guardada en: {path_debug}")
            imagen.debug_counter += 1

        # guardar imagenes en carpeta del path si está la opción activada
        if settings.IMAGEN_GUARDAR:
            path_res = os.path.join(self.fichero.path_base, f"{self.__class__.__name__}_{self.fichero.pin}_resultado_puntos_info.{settings.FORMATO_GUARDAR_RES}")
            self.imagen = self.imagen.guardar(path_res, usar_original=True)
            self.logger.log(f"Imagen CAM resultado puntos, guardada en:: {path_res}")

            path_res = os.path.join(self.fichero.path_base, f"{self.__class__.__name__}_{self.fichero.pin}_resultado_segmentos_info.{settings.FORMATO_GUARDAR_RES}")
            cv2.imwrite(path_res, img_copy)
            self.logger.log(f"Imagen CAM resultado segmentos, guardada en:: {path_res}")


    #Función para dibujar una máscara semitransparente en las zonas que ha detectado masilla sobre la imagen original
    def _mascara_transparente(self, mask, color=(0, 0, 255), alpha=0.4):

        # La máscara de entrada es en 3 canales, (255,255,255) cuando es fondo, y (0,0,0) cuando es masilla. Se definió así por la necesidad de dibujar los cordones encima en otro color para un resultado intermedio
        mask_bool = np.any(mask == 0, axis=-1)   # se crea una máscara donde cada píxel es True si algún canal vale 0, en la máscara devuelta por la red U-Net

        # preparar
        overlay_color = np.empty_like(self.imagen.original)       # se crea una imagen del mismo tamaño que la original
        overlay_color[:] = color                                   # se rellena con el color indicado

        # mezcla la imagen original (1-alfa) y la máscara generada (alfa) solo en la región que tiene la máscara activa (donde hay predicción de masilla)
        self.imagen.original[mask_bool] = (                     # con imagen.original[mask_bool] se seleccionan solo los píxeles donde mask_bool == True
                alpha * overlay_color[mask_bool].astype(np.float32)         # se convierte a float32 para evitar errores por desbordamiento
                + (1 - alpha) * self.imagen.original[mask_bool].astype(np.float32)
        ).astype(np.uint8)                                  # se vuelve a dejar en uint8

        if settings.IMAGEN_DEBUG:
            ruta = os.path.join(os.path.dirname(self.path_debug), "debug")
            os.makedirs(ruta, exist_ok=True)
            path_debug = os.path.join(ruta, f"{imagen.debug_counter}_mascara_transparente.{settings.FORMATO_GUARDAR_DEBUG}")
            cv2.imwrite(path_debug, self.imagen.original)
            self.logger.log(f"Imagen de debug guardada en: {path_debug}")
            imagen.debug_counter += 1

    # Función que modifica los cordones según la matriz de transformación (rotación + traslación) calculada anteriormente, e interpola para hacer que cada punto sea un pixel
    @staticmethod
    def _modificar_cordones(cordones, matriz):

        cordones_resultado = []
        for cordon in cordones:
            cordon_np = np.array(cordon, dtype=np.float32)      # se convierte cada cordón a float32 para entrada cv2.transform
            if cordon_np.ndim != 2 or cordon_np.shape[1] != 2:   # comprobar que el cordón tiene 2 dimensiones
                raise ValueError(f"Formato de cordón inválido: se esperaba (N, 2), se obtuvo {cordon_np.shape}")
            # Transformar con la matriz
            cordon_aux = cordon_np.reshape((-1, 1, 2))
            cordon_modif_aux = cv2.transform(cordon_aux, matriz)
            cordon_modif = np.round(cordon_modif_aux.reshape((-1, 2))).astype(int)
            # Interpolar
            cordon_interp = []
            for i in range(len(cordon_modif) - 1):
                x0, y0 = cordon_modif[i]
                x1, y1 = cordon_modif[i + 1]
                dist = math.hypot(x1 - x0, y1 - y0)
                pasos = max(1, int(dist))  # al menos 1 paso
                for t in np.linspace(0, 1, pasos):
                    x = int(round(x0 * (1 - t) + x1 * t))
                    y = int(round(y0 * (1 - t) + y1 * t))
                    cordon_interp.append((x, y))
            cordones_resultado.append(cordon_interp)
        return cordones_resultado
