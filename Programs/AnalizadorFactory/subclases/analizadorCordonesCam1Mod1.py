from analizadorCordonesBase import AnalizadorCordonesBase
import settings
import imagen

class AnalizadorCordonesCam1Mod1(AnalizadorCordonesBase):

    def __init__(self, config, path_img, logger, fichero):
        super().__init__(config, path_img, logger, fichero)
        self.patron = imagen.Imagen(config['path_patron'], self.logger)
        self._resPos = None  # resultado de posicion: centro, diferencia con el centro inicial, y resultado booleano
        self._resAng = None  # resultado de angulo: valor angulo grados, diferencia con el ángulo inicial y resultado booleano
        self._resMatriz = None # matriz traslación-rotación resultante
        self.cordones_modificados = None
        self.imagen_mascara = None  # crear np.array para máscara, con píxeles blancos que precide la FCN U-Net
        self.resultado = None  # diccionario con los puntos malos, los segmentos malos, y por cordon: puntos malos, puntos malos con coordenadas, y segmentos malos expresados en % sobre la longitud del cordón

    def localizar(self):
        #localizar la posición del patrón1 en la carrocería
        roi = self.config['cfg_ini']['ROI_POS_INI']
        pos_ini = self.config['cfg_ini']['POSICION_INI']
        patron = self.patron
        self._resPos = self._posicion(roi, pos_ini, patron)     #metodo posicion
        pos_centro, pos_dif_centro, pos_ok, porcent = self._resPos

        #localizar el ángulo en la carrocería
        if pos_ok:    #si el resultado de posición es bueno, sigue
            self._resAng = self._angulo(self.config['cfg_ini']['ROI_ANG_INI'], pos_dif_centro)
            ang_valor, ang_dif, ang_ok = self._resAng
        else:
            raise ValueError(f"Análisis abortado por fallo al localizar la posición del patrón en la carrocería: {self.path_img}")

        # Calcular la matriz de traslación-rotación con patrón1 y ángulo
        if ang_ok and pos_ok:    #si el resultado del ángulo es bueno, sigue
            self._resMatriz = self._matriz(pos_centro, pos_dif_centro, ang_dif)
        else:
            raise ValueError(f"Análisis abortado por fallo al localizar el ángulo en la carrocería: {self.path_img}")

    def modificar(self):
        # Dibujar los cordones originales, calcular los modificados con la matriz1 y dibujarlos
        if settings.DIBUJAR_CORDONES_ORIGINALES:
            self._dibujar_cordones(self.cordones, settings.COLOR_NEGRO, grosor=1, nombre="Cordones_originales")
        self.cordones_modificados = self._modificar_cordones(self.cordones, self._resMatriz)
        self._dibujar_cordones(self.cordones_modificados, settings.COLOR_CORDON, grosor=1, nombre="Cordones_modificados_matriz1")

        #Dibujar ventanas de recorte que van a servir como entrada del analizador
        self._dibujar_ventanas_recortes_analisis()

    def analizar(self):
        #Máscara de masilla que predice la FCN U-Net
        imagen_mascara = self._analizar_modelo(self.cordones_modificados)      #self.imagen_mascara -> resultado de la máscara devuelta por la FCN U-Net

        #Dibujar una máscara de masilla semitransparente sobre la imagen original
        self._mascara_transparente(imagen_mascara, settings.COLOR_CORDON, alpha=0.4)

        #Diccionario donde se indica el número de puntos con fallo, de segmentos con fallo y los datos por cordón, con las cordenadas y los segmentos normalizados entre 0 y 1
        self.resultado = self._calcular_resultado(imagen_mascara, self.cordones_modificados)

    def finalizar(self):
        self._guardar_resultado(self.resultado)
        return self.resultado

    # metodo abstracto en AnalizadorCordonesBase
    def _buscar_angulo(self, roi1, roi2, roi_x1, roi_y1, roi_x2, roi_y2, roi_w, roi_h, umbral_res):
        return self._buscar_angulo_vertical(roi1, roi2, roi_x1, roi_y1, roi_x2, roi_y2, roi_w, roi_h, umbral_res)



