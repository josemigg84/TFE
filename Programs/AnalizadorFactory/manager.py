# manager.py
class AnalisisManager:
    def __init__(self, factoria, config, path_img, logger, fichero):
        self.analizador = factoria.crear(config, path_img, logger, fichero)
        self.logger = logger

    def ejecutar(self):
        try:
            self.analizador.localizar()
            self.analizador.modificar()
            self.analizador.analizar()
            res = self.analizador.finalizar()
            return res
        except Exception as e:
            self.logger.log(f"Error durante el análisis: {e}")
            raise
