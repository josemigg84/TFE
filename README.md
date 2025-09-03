# Sistema de visión artificial para la inspección de la aplicación de cordones de masilla en un proceso industrial
Este trabajo forma parte del trabajo fin de estudios (**TFE**) del Grado en Ingeniería Informática de [**UNIR**](http://www.unir.net)
## Resumen 
El presente trabajo aborda un problema de inspección de calidad en un proceso de fabricación industrial real. La solución planteada consiste en un sistema de verificación automática de los cordones de masilla aplicados en las carrocerías para sellar el habitáculo interior, utilizando técnicas de visión artificial basadas en redes neuronales profundas.
Se propone una aplicación de segmentación semántica implementada mediante una arquitectura de red U-Net, que genera máscaras con las zonas de la imagen en las que se ha aplicado masilla. Posteriormente, otro algoritmo verifica si la masilla se encuentra correctamente ubicada, garantizando el adecuado sellado de las carrocerías. Para el entrenamiento del modelo, se ha utilizado un dataset propio, generado con imágenes de las cámaras de inspección, y debido al reducido volumen y a la escasa variabilidad de los datos, se han utilizado técnicas de data augmentation que han aportado robustez al sistema y han evitado el sobreajuste del modelo durante la fase de entrenamiento.
Los adecuados resultados obtenidos, con métricas (IoU=0,98) aunque preliminares, indican la viabilidad de la solución aportada y la robustez del sistema frente a diferentes condiciones de iluminación. La principal aportación de este trabajo radica en la aplicación práctica de técnicas de segmentación semántica a un problema real de inspección en la industria del automóvil, demostrando que es posible desarrollar este tipo de soluciones con medios propios de la empresa y alcanzar resultados satisfactorios.
## Índice
- [Requerimientos técnicos del software](#requerimientos-técnicos-del-software)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Generación del dataset y entrenamiento](#generación-del-dataset-y-entrenamiento)
- [Simulación](#simulación)
- [Resultado esperado](#resultado-esperado)

## Requerimientos técnicos del software
1.	**Lenguaje y versión**: El software se ha desarrollado utilizando la versión de **Python 3.11.3**. No obstante para herramientas auxiliares como **Labelme** o **Albumentations**, se han empleado entornos adicionales con otras versiones. Se recomienda utilizar estas mismas versiones para asegurar la compatibilidad del sistema, aunque en algunos casos versiones anteriores también pueden ser válidas.
2.	**Entorno de ejecución**: Para el desarrollo de este trabajo se han utilizado diferentes entornos virtuales de **Anaconda**. Se ha utilizado un entorno principal para la ejecución general del sistema, pero por problema de compatibilidades de paquetes se han utilizados dos entornos virtuales más, uno para la herramienta **labelme** y otro para **Albumentations**. Se recomienda el uso de entornos virtuales (por ejemplo **Anaconda** o **venv**) que permitan instalar las dependencias necesarias para ejecutar el software.
3.	**Motor de la base de datos**: MySQL Community Server – GPL, versión 8.2.0
Aunque no es un requisito, para la pruebas se recomienda el uso de un contenedor **Docker** por su sencillez.

### Instalación del entorno principal

1. **Instalar Anaconda**  
   [Descargar Anaconda](https://www.anaconda.com/download)

2. **Crear un entorno virtual y activarlo** (ejemplo con nombre `TFG`):  
    ~~~
   conda create -n TFG python=3.11.3
   conda activate TFG
    ~~~
2. **Instalar dependencias principales** (instalar individualmente via pip dentro del entorno):  
    ~~~
   pip install python-snap7==2.0.2
   pip install opencv-python==4.11.0.86
   pip install matplotlib==3.10.5
   pip install mysql-connector-python==9.4.0
   pip install python-dotenv==1.1.1
   pip install tensorflow==2.20.0
    ~~~


## Estructura del proyecto


## Generación del dataset y entrenamiento


## Simulación


## Resultado esperado
