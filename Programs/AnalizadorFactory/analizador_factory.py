# factory_base.py
from abc import ABC, abstractmethod

class AnalizadorFactoryMethod(ABC):
    @abstractmethod
    def crear(self, config, path_img, logger, fichero):
        pass
