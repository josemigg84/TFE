# Sistema de visión artificial para la inspección de la aplicación de cordones de masilla en un proceso industrial
Este trabajo forma parte del trabajo fin de estudios (**TFE**) del Grado en Ingeniería Informática de [**UNIR**](http://www.unir.net)
## Resumen 
El presente trabajo aborda un problema de inspección de calidad en un proceso de fabricación industrial real. La solución planteada consiste en un sistema de verificación automática de los cordones de masilla aplicados en las carrocerías para sellar el habitáculo interior, utilizando técnicas de visión artificial basadas en redes neuronales profundas.
Se propone una aplicación de segmentación semántica implementada mediante una arquitectura de red U-Net, que genera máscaras con las zonas de la imagen en las que se ha aplicado masilla. Posteriormente, otro algoritmo verifica si la masilla se encuentra correctamente ubicada, garantizando el adecuado sellado de las carrocerías. Para el entrenamiento del modelo, se ha utilizado un dataset propio, generado con imágenes de las cámaras de inspección, y debido al reducido volumen y a la escasa variabilidad de los datos, se han utilizado técnicas de data augmentation que han aportado robustez al sistema y han evitado el sobreajuste del modelo durante la fase de entrenamiento.
Los adecuados resultados obtenidos, con métricas (IoU=0,98) aunque preliminares, indican la viabilidad de la solución aportada y la robustez del sistema frente a diferentes condiciones de iluminación. La principal aportación de este trabajo radica en la aplicación práctica de técnicas de segmentación semántica a un problema real de inspección en la industria del automóvil, demostrando que es posible desarrollar este tipo de soluciones con medios propios de la empresa y alcanzar resultados satisfactorios.
## 📑 Índice
- [Requerimientos técnicos del software](#requerimientos-tecnicos-del-software)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Generación del dataset y entrenamiento](#generacion-del-dataset-y-entrenamiento)
- [Simulación](#simulacion)

## Requerimientos tecnicos del software
Aquí explicas dependencias (Python, Anaconda, MySQL, Docker...).

## Estructura del proyecto
Aquí muestras el árbol de carpetas.

## Generacion del dataset y entrenamiento
Aquí explicas cómo crear el dataset y entrenar el modelo.

## Simulacion
Aquí explicas cómo ejecutar la simulación.
