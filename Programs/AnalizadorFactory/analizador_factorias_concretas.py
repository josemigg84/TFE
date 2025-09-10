from analizador_factory import AnalizadorFactoryMethod
from subclases.analizadorCordonesCam1Mod1 import AnalizadorCordonesCam1Mod1
from subclases.analizadorCordonesCam1Mod2 import AnalizadorCordonesCam1Mod2
from subclases.analizadorCordonesCam2Mod1 import AnalizadorCordonesCam2Mod1
from subclases.analizadorCordonesCam2Mod2 import AnalizadorCordonesCam2Mod2

# Factoría para crear analizadores de cordones de Cámara 1 Modelo 1
class AnalizadorCordonesCam1Mod1Factory(AnalizadorFactoryMethod):
    def crear(self, config, path_img, logger, fichero):
        return AnalizadorCordonesCam1Mod1(config, path_img, logger, fichero)    # Devuelve una instancia del analizador concreto Cam1Mod1

# Factoría para crear analizadores de cordones de Cámara 1 Modelo 2
class AnalizadorCordonesCam1Mod2Factory(AnalizadorFactoryMethod):
    def crear(self, config, path_img, logger, fichero):
        return AnalizadorCordonesCam1Mod2(config, path_img, logger, fichero)    # Devuelve una instancia del analizador concreto Cam1Mod2

# Factoría para crear analizadores de cordones de Cámara 2 Modelo 1
class AnalizadorCordonesCam2Mod1Factory(AnalizadorFactoryMethod):
    def crear(self, config, path_img, logger, fichero):
        return AnalizadorCordonesCam2Mod1(config, path_img, logger, fichero)   # Devuelve una instancia del analizador concreto Cam2Mod1

# Factoría para crear analizadores de cordones de Cámara 2 Modelo 2
class AnalizadorCordonesCam2Mod2Factory(AnalizadorFactoryMethod):
    def crear(self, config, path_img, logger, fichero):
        return AnalizadorCordonesCam2Mod2(config, path_img, logger, fichero)  # Devuelve una instancia del analizador concreto Cam2Mod2

