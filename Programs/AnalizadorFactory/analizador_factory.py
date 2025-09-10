from abc import ABC, abstractmethod

# clase abstracta para factorias de analizadores
class AnalizadorFactoryMethod(ABC):
    @abstractmethod
    # metodo abstracto que deben implementar las factorías concretas
    def crear(self, config, path_img, logger, fichero):
        pass
