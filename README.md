# Sistema de visión artificial para la inspección de la aplicación de cordones de masilla en un proceso industrial
Este trabajo forma parte del trabajo fin de estudios (**TFE**) del Grado en Ingeniería Informática de [**UNIR**](http://www.unir.net)
## Resumen 
El presente trabajo aborda un problema de inspección de calidad en un proceso de fabricación industrial real. La solución planteada consiste en un sistema de verificación automática de los cordones de masilla aplicados en las carrocerías para sellar el habitáculo interior, utilizando técnicas de visión artificial basadas en redes neuronales profundas.
Se propone una aplicación de segmentación semántica implementada mediante una arquitectura de red U-Net, que genera máscaras con las zonas de la imagen en las que se ha aplicado masilla. Posteriormente, otro algoritmo verifica si la masilla se encuentra correctamente ubicada, garantizando el adecuado sellado de las carrocerías. Para el entrenamiento del modelo, se ha utilizado un dataset propio, generado con imágenes de las cámaras de inspección, y debido al reducido volumen y a la escasa variabilidad de los datos, se han utilizado técnicas de data augmentation que han aportado robustez al sistema y han evitado el sobreajuste del modelo durante la fase de entrenamiento.
Los adecuados resultados obtenidos, con métricas (IoU=0,98) aunque preliminares, indican la viabilidad de la solución aportada y la robustez del sistema frente a diferentes condiciones de iluminación. La principal aportación de este trabajo radica en la aplicación práctica de técnicas de segmentación semántica a un problema real de inspección en la industria del automóvil, demostrando que es posible desarrollar este tipo de soluciones con medios propios de la empresa y alcanzar resultados satisfactorios.
## Índice
- [1. Requerimientos técnicos del software](#1-requerimientos-técnicos-del-software)
- [2. Estructura del proyecto](#2-estructura-del-proyecto)
- [3. Generación del dataset](#3-generación-del-dataset)
- [4. Entrenamiento del modelo U-Net](#4-entrenamiento-del-modelo-u-net)
- [5. Simulación](#5-simulación)

## 1. Requerimientos técnicos del software
- **Lenguaje y versión**: El software se ha desarrollado utilizando la versión de **Python 3.11.3**. No obstante para herramientas auxiliares como **Labelme** o **Albumentations**, se han empleado entornos adicionales con otras versiones. Se recomienda utilizar estas mismas versiones para asegurar la compatibilidad del sistema, aunque en algunos casos versiones anteriores también pueden ser válidas.
- **Entorno de ejecución**: Para el desarrollo de este trabajo se han utilizado diferentes entornos virtuales de **Anaconda**. Se ha utilizado un entorno principal para la ejecución general del sistema, pero por problema de compatibilidades de paquetes se han utilizado dos entornos virtuales más, uno para la herramienta **labelme** y otro para **Albumentations**. Se recomienda el uso de entornos virtuales (por ejemplo **Anaconda** o **venv**) que permitan instalar las dependencias necesarias para ejecutar el software.
- **Motor de la base de datos**: MySQL Community Server – GPL, versión 8.2.0
Aunque no es un requisito, para las pruebas se recomienda el uso de un contenedor **Docker** por su sencillez.

### Paso 1. Instalación del entorno principal
1. **Instalar Anaconda** desde el sitio oficial:
   [Descargar Anaconda](https://www.anaconda.com/download)

3. **Crear un entorno virtual y activarlo** (ejemplo con nombre `TFG`):  
    ~~~
   conda create -n TFG python=3.11.3
    ~~~
    ~~~
   conda activate TFG
    ~~~
2. **Instalar dependencias principales** (instalar individualmente via pip dentro del entorno):  
    ~~~
   pip install python-snap7==2.0.2
    ~~~
    ~~~
   pip install opencv-python==4.11.0.86
    ~~~
    ~~~
   pip install matplotlib==3.10.5
    ~~~
    ~~~
   pip install mysql-connector-python==9.4.0
    ~~~
    ~~~
   pip install python-dotenv==1.1.1
    ~~~
    ~~~
   pip install tensorflow==2.20.0
    ~~~

### Paso 2. Instalación del entorno de etiquetado de imágenes
1. **Crear un entorno virtual y activarlo** (ejemplo con nombre `etiquetado`):  
    ~~~
   conda create -n etiquetado python=3.8
    ~~~
    ~~~
   conda activate etiquetado
    ~~~
2. **Instalar dependencias necesarias** (instalar individualmente via pip dentro del entorno):
  
   **pyside2** (para la interfaz gráfica, instalado via conda-forge):
    ~~~
   conda install -c conda-forge pyside2
    ~~~
   **labelme** (instalado via pip):
    ~~~
   pip install labelme
    ~~~

### Paso 3. Instalación del entorno para data augmentation
1. **Crear un entorno virtual y activarlo** (ejemplo con nombre `albumentations`):  
    ~~~
   conda create -n albumentations python=3.8
    ~~~
    ~~~
   conda activate albumentations
    ~~~
2. **Instalar dependencias necesarias** (instalar individualmente via pip dentro del entorno):

   **albumentations** (instalado via pip):
    ~~~
   pip install albumentations
    ~~~
   **opencv-python** (versión completa: necesaria para soporte gráfico, evitando instalar opencv-python-headless):
    ~~~
   pip install opencv-python
    ~~~

### Paso 4. Instalación de la base de datos MySQL con Docker
1. **Descargar Docker Desktop desde la web oficial:**  
[Descargar Docker](https://www.docker.com)
2. **Descargar algún gestor de bases de datos**. Para este proyecto se ha utilizado **DataGrip de JetBrains**, pero se puede utilizar cualquier otro válido para **MySQL.**
   **Datagrip** se puede descargar desde la web oficial: 
[Descargar DataGrip](https://www.jetbrains.com/es-es/datagrip)
3. Ejecutar este comando para descargar la imagen **de MySQL versión 8.2**:
    ~~~
   docker pull mysql:8.2.0
    ~~~
4. Con el siguiente comando, **crear un contenedor** a partir de la imagen descargada que exponga el **puerto 3306** del contenedor en el **puerto 3306** de nuestra máquina local (puerto por defecto). A modo de ejemplo, el nombre del contenedor se pone como TFE y el password del usuario root: mysql (estos ajustes se pueden personalizar):
    ~~~
   docker run -p 3306:3306 --name TFE -e MYSQL_ROOT_PASSWORD=mysql -d mysql:8.2.0
    ~~~
5. Abrir el **gestor de base de datos**, **crear un nuevo schema** y **ejecutar en consola los scripts** que se encuentran en el directorio BBDD de este repositorio en este orden:
   - **Script DDL** genera las tablas y sus relaciones, además de crear un índice.
   - **Script DML** inserta los valores fijos de configuración necesarios antes de insertar datos desde el programa de resultados.


## 2. Estructura del proyecto
El flujo principal de este proyecto se divide en **3 programas independientes**:
1. Comunicación con el **PLC** y las **cámaras** para capturar imágenes de las carrocerías.  
2. Análisis de las imágenes y generación del resultado.  
3. Inserción del resultado en la **base de datos**.

Para implementar esta solución, la **arquitectura propuesta** se basa en un modelo de **tuberías y filtros** (pipes and filters), donde cada módulo se comporta como un filtro especializado y se conecta con los siguientes a través de **colas FIFO con persistencia en disco**. De esta forma, se desacoplan los procesos asegurando una mejor tolerancia a fallos si un proceso se detiene, los demás permanecen acumulando datos en la cola o esperando a recibirlos.

![Arquitectura](/docs/TFG_Arquitectura.png)

Por ello es importante **respetar la estructura de directorios** de este repositorio tal y como se indica a continuación, descargando el código completo y guardándolo en el equipo con la misma estructura. El directorio raíz se llama TFE a modo de ejemplo.

~~~
TFE/
├── Programs/
│   ├── AnalizadorFactory/    # Programa del analizador de imágenes
│   ├── Grabar_imagenes/      # Programa de grabación de imágenes
│   ├── Resultados/           # Programa de inserción en la BBDD
│   ├── Scripts/              # Herramientas auxiliares como la generación del dataset o el entrenamiento del modelo
├── data/                # La estructura data se genera sola si no existe.
│   ├── App/         
│   ├── ├── Local/         
│   ├── ├── ├── ordenes/        
│   ├── ├── ├── ├── fifo_analizar_resultados/          # Cola fifo de ficheros JSON entre analizar y resultados
│   ├── ├── ├── ├── fifo_analizar_resultados_fallos/   # Ficheros JSON con fallo en la cola FIFO analizar-resultados
│   ├── ├── ├── ├── fifo_grabar_analizar/              # Cola fifo de ficheros JSON entre grabar y analizar
│   ├── ├── ├── ├── fifo_grabar_analizar_fallos/       # Ficheros JSON con fallo en la cola FIFO grabar-analizar
├── images/              # Directorio de imágenes organizado en carpetas por año, mes, dia y número de pin de la carrocería.
│   ├── "año"/           # La estructura de images se genera sola si no existe.
│   ├── ├──  "mes"/
│   ├── ├── ├── "dia"/
│   ├── ├── ├── ├── "pin"/
├── logs/                # Directorio de logs organizado en carpetas por año, mes, y dia.
│   ├── "año"/           # La estructura de logs se genera sola si no existe.
│   ├── ├──  "mes"/
│   ├── ├── ├── "dia"/
│   ├── ├── ├── ├── "pin"/ 
├── models/              # Contiene el modelo entrenado de la red neuronal U-Net
├── patrones/            # Contiene los patrones de referencia
~~~
### A continuación se muestran los diagramas de clases UML de los diferentes programas y el modelo entidad relación (ER) de la BBDD

**Diagrama de clases UML del proceso de grabación de imágenes**
![UMLGrabar](/docs/GrabarUML.png)

**Diagrama de clases UML del proceso de análisis de imágenes**
![UMLAnalizar](/docs/AnalizarUML_FactoryMethod.png)

**Diagrama de clases UML del proceso de grabación del resultado**
![UMLResultados](/docs/ResultadosUML.png)

**Modelo Entidad-Relación de la capa de persistencia**
![MOdeloER](/TFG.drawio.png)

## 3. Generación del dataset
Para este TFE se ha utilizado un **dataset propio**, obtenido a partir de imágenes capturadas con las cámaras de inspección.
El proceso incluyó:

   - **Recorte** de las zonas de interés.

   - **Etiquetado** para diferenciar la clase masilla del fondo.

   - Aplicación de **técnicas de aumentación de datos** para incrementar la variabilidad del conjunto.

La estructura final del dataset se puede observar en el siguiente directorio:
~~~
TFE/
├── dataset/
│   ├── images/    # donde se encuentran las imágenes
│   ├── masks/     # donde se encuentran las máscaras
~~~

Para la generación del dataset se han seguido los siguientes pasos:
### Paso 1. Recorte de las imágenes
Se debe ejecutar el Script "Recortar.py" bajo el entorno virtual `albumentations` creado anteriormente.
~~~
TFE/
├── Programs/
│   ├── Scripts/            
│   ├── ├──  "Recortar.py"/
~~~
Previamente, se debe ajustar dentro del script el path de entrada (imágenes originales) y salida de imágenes (recortes).
Se pueden realizar recortes por lotes de imágenes del mismo tipo, por lo que estás deben estar organizadas por tipo de cámara y modelo previamente.
Dentro del script se debe ajustar ese tipo de configuración de cámara y modelo utilizada.
Además los recortes salen numerados desde el valor de una variable llamada `inicio`. Por defecto ese valor está a 1, pero si se realizan varios lotes, se debe ajustar al valor siguiente al número de recortes ya realizados, para evitar que se sobreescriban.

### Paso 2. Etiquetado de las imágenes
Se debe activar el entorno virtual `etiquetado` creado anteriormente y ejecutar la interfaz gráfica de usuario (GUI) del programa.
   ~~~
    conda activate etiquetado
   ~~~
   ~~~
    labelme
   ~~~
Una vez arrancado el programa se deben etiquetar manualmente todos los recortes, lo que genera un JSON para cada uno de ellas.

### Paso 3. Ejecución del script que genera la máscara resultante
Se debe activar el entorno virtual `etiquetado` creado anteriormente y ejecutar el Script "dataset_procesar_json.py" que se encuentra en el directorio:
~~~
TFE/
├── Programs/
│   ├── Scripts/            
│   ├── ├──  "dataset_procesar_json.py"/
~~~
Previamente, se debe ajustar dentro del script el path de entrada, donde se encuentran los ficheros JSON.
Esto llama a un comando interno del programa Labelme, para cada uno de los ficheros JSON generados, evitando tener que hacerlo manualmente uno a uno.
El resultado es el mismo que hacerlo de forma individual, se genera una carpeta con varios ficheros dentro, y dentro de ella se encuentra la máscara resultante con el nombre `label.png`

### Paso 4. Copia y renombrado de cada una de las máscaras con el mismo nombre que la imagen de recorte
Se debe activar el entorno virtual `etiquetado` creado anteriormente y ejecutar el Script `dataset_renombrar_label.py` que se encuentra en el directorio:
~~~
TFE/
├── Programs/
│   ├── Scripts/            
│   ├── ├──  "dataset_renombrar_label.py"/
~~~
Previamente, se debe ajustar dentro del script el path de entrada, donde se encuentran las carpetas y el path de salida donde se desea guardar las máscaras.
Las carpetas creadas en el paso anterior tienen la forma `nombre_json`, siendo nombre el numero de imagen de recorte original.
La ejecución de este script copia el fichero `label.png` incluido dentro de la carpeta y lo renombra con el mismo número de la imagen de recorte, el cual se extrae del nombre de la carpeta. Esto permite mantener correctamente la referencia entre imagen y máscara.

### Paso 5. Uso de técnicas de aumentación de datos
Se debe activar el entorno virtual `albumentations` creado anteriormente y ejecutar el Script `Albumentations.py` que se encuentra en el directorio:
~~~
TFE/
├── Programs/
│   ├── Scripts/            
│   ├── ├──  "Albumentations.py"/
~~~
Con las dos carpetas, la de imágenes y máscaras ya generadas en los pasos previos, ahora se ajusta dentro de este script el path de entrada de imagenes y máscaras, además de los dos path de salida.
Dentro del script se han configurado 29 transformaciones de imágenes, además de guardar la imagen original. Las parejas de imagen/máscara resultantes se nombran de forma aleatoria con un dígito de 6 cifras, evitando que el orden de entrada de las imágenes en los lotes de entrenamiento afecte a los datos de validación del mismo.

Con estos pasos, se han generado un total de 8010 imágenes con sus máscaras correspondientes para poder entrenar la red neuronal U-Net.

## 4. Entrenamiento del modelo U-Net
El modelo de segmentación está basado en la **arquitectura U-Net**, con un dataset propio de 8010 imágenes y máscaras, dividido en **80% para entrenamiento** y **20% para validación**.

**Configuración principal**:

   - **Tamaño de imagen**: 256x256 px

   - **Batch size**: 8

   - **Épocas**: 20

   - **Optimizador**: Adam

   - **Función de pérdida**: Binary Cross-Entropy

   - **Métricas**: Accuracy, Binary IoU

El mejor modelo alcanzó un IoU ≈ 0.98, demostrando la viabilidad de la solución en un entorno industrial.
Para el entrenamiento se debe activar el entorno virtual `TFG` creado anteriormente y ejecutar el Script `entrenar.py` que se encuentra en el directorio:
~~~
TFE/
├── Programs/
│   ├── Scripts/            
│   ├── ├──  "entrenar.py"/
~~~
**NOTA**: EL código de ejecución del script es totalmente compatible con el uso de GPU con CUDA y TensorFlow, pero es necesario adecuar previamente el entorno virtual de Anaconda instalando las versiones compatibles con CUDA y cuDNN, así como la versión de TensorFlow que soporte aceleración por GPU, de acuerdo con las características de la tarjeta gráfica del equipo. En el caso de este trabajo, debido a limitaciones técnicas de la GPU disponible, el entrenamiento del modelo se ha realizado utilizando la CPU y por ello, el entorno virtual generado anteriormente no incluye el soporte de CUDA y cuDNN. 


## 5. Simulación
Para la ejecución de los programas en un entorno real o la simulación que aquí se propone es necesario crear previamente varios ficheros de variables de entorno `.env` donde se configuran nombres de usuario, contraseñas, o direcciones IP que no están reflejadas en el código por motivos obvios.
### Para el programa de grabación de imágenes, que se presenta en el siguiente directorio:
~~~
TFE/
├── Programs/
│   ├── Grabar_imagenes/            
~~~
Se necesita crear un fichero `.env` como el que se muestra de ejemplo `.env.example` dentro del mismo directorio. En este fichero se configuran las variables de usuario, contraseña, y las direcciones IP de las cámaras y PLC. Lo que se muestra a continuación es un ejemplo:
   ~~~
    USUARIO="user"
    PASSWORD="1234"
    IP_CAM_1="192.168.0.2"
    IP_CAM_2="192.168.0.3"
    PLC_IP='192.168.0.10'
   ~~~

### Para el programa de grabación de resultados en la base de datos, que se presenta en el siguiente directorio:
~~~
TFE/
├── Programs/
│   ├── Resultados/            
~~~
Se necesita crear un fichero `.env` como el que se muestra de ejemplo `.env.example` dentro del mismo directorio. En este fichero se configuran las variables de conexión a la base de datos. Lo que se muestra a continuación es un ejemplo:
   ~~~
    MYSQL_HOST=localhost
    MYSQL_USER=root
    MYSQL_PASSWORD=mysql
    MYSQL_DATABASE=TFG
    PORT=3306
   ~~~

### Restricciones en la simulación:
Como la arquitectura de este trabajo se divide en 3 programas independientes, hay que tener en cuenta varias restricciones a la hora de simular el funcionamiento:
   - **Programa de grabación de imágenes**: Se puede simular la comunicación con el PLC, mediante software propietario de **SIEMENS**, junto con su simulador de PLCs y en combinación con la herramienta `NetToPLCsim`, que actúa a modo de servidor intermedio. Este programa permite establecer comunicación con el simulador como si se tratara de un PLC real. Sin embargo, no es posible simular el modelo de cámaras utilizado ni las imágenes capturadas de forma realista, por lo que este programa no se tendrá en cuenta dentro de la simulación.
   - **Programa de análisis de imágenes**: Este programa sí puede simularse dentro de este entorno, siempre que previamente se hayan seguido los pasos descritos para la creación de los entornos virtuales, la descarga del repositorio y el almacenamiento del mismo respetando la estructura de directorios indicada.
   - **Programa de grabación de resultados**: Para su simulación es necesario haber instalado previamente el motor y el gestor de la base de datos, tal y como se indica en el paso 4 del punto 1. Aunque la base de datos no resulta imprescindible para visualizar el funcionamiento básico de la simulación, sí lo es para el posterior almacenamiento y tratamiento de la información registrada en la BBDD.

### Detalles de la simulación
Como no se puede simular el programa de grabación de imágenes, se parte de esta situación inicial:
   - **Dentro del directorio donde se guardan los ficheros JSON de la cola FIFO entre el proceso de grabación y el de análisis, hay ya 10 ficheros preparados con la información relativa a 10 carrocerías pendientes de analizar. Son 5 de cada modelo.**
      ~~~
       TFE/
       ├── data/
       │   ├── App/
       │   ├── ├── Local/
       │   ├── ├── ├── ordenes/
       │   ├── ├── ├── ├── fifo_grabar_analizar/
       │   ├── ├── ├── ├── ├── 6320011_in.json/
       │   ├── ├── ├── ├── ├── 6320011_in.json/
       │   ├── ├── ├── ├── ├── 6320012_in.json/
       │   ├── ├── ├── ├── ├── 6320013_in.json/
       │   ├── ├── ├── ├── ├── 6320014_in.json/
       │   ├── ├── ├── ├── ├── 6320015_in.json/
       │   ├── ├── ├── ├── ├── 6320021_in.json/
       │   ├── ├── ├── ├── ├── 6320022_in.json/
       │   ├── ├── ├── ├── ├── 6320023_in.json/
       │   ├── ├── ├── ├── ├── 6320024_in.json/
       │   ├── ├── ├── ├── ├── 6320025_in.json/
      ~~~
   - **Dentro del directorio donde se guardan las imágenes, hay 10 carpetas con el nombre del número de pin de cada carrocería pendiente de analizar.**
      ~~~
       TFE/
       ├── images/
       │   ├── 2025/
       │   ├── ├── 08/
       │   ├── ├── ├── 13/
       │   ├── ├── ├── ├── 6320011/
       │   ├── ├── ├── ├── 6320012/
       │   ├── ├── ├── ├── 6320013/
       │   ├── ├── ├── ├── 6320014/
       │   ├── ├── ├── ├── 6320015/      
       │   ├── ├── ├── ├── 6320021/
       │   ├── ├── ├── ├── 6320022/
       │   ├── ├── ├── ├── 6320023/
       │   ├── ├── ├── ├── 6320024/      
       │   ├── ├── ├── ├── 6320025/
      ~~~
   - **Cada carpeta incluye dos imágenes, una de cada lado de la carrocería y están correctamente nombradas como lo haría el programa de grabación. Como ejemplo se muestra el directorio para el primer pin**
      ~~~
       TFE/
       ├── images/
       │   ├── 2025/
       │   ├── ├── 08/
       │   ├── ├── ├── 13/
       │   ├── ├── ├── ├── 6320011/
       │   ├── ├── ├── ├── ├── c1_6320011.jpg/
       │   ├── ├── ├── ├── ├── c2_6320011.jpg/
      ~~~
   - **Las 4 primeras carrocerías de cada modelo tienen los cordones bien aplicados, mientras que la quinta de cada modelo, es decir, las carrocerías 5 y 10 tienen los cordones desviados.**

   - **El simulador tiene múltiples opciones configurables desde el fichero `settings.py`, de las cuales se muestran algunas a continuación:**
      ~~~
       IMAGEN_GUARDAR = True               #OPCION DE GUARDAR O NO LAS IMAGENES RESULTANTES, POR ESPACIO
       IMAGEN_DEBUG = True                 #OPCION DE GUARDAR TODAS LAS TRANSFORMACIONES DE IMAGENES. Cada vez que se ejecuta se sobreescriben
       COPIA_JSON_IN_OUT = True            #Opción que copia el json de entrada y de salida en la carpeta de resultados de imagen
       DIBUJAR_VENTANAS_RECORTE = True    #OPCION DE DIBUJAR EN LA IMAGEN LAS VENTANAS QUE SE RECORTAN PARA LA FCN
       DIBUJAR_CORDONES_ORIGINALES = False  # == True dibuja en la imagen los cordones orginales y los modificados; ==False solo dibuja los cordones modificados
       FORMATO_GUARDAR_RES = "png" #png o jpg
       FORMATO_GUARDAR_DEBUG = "png"
       FORMATO_GUARDAR_MASK = "png"
      ~~~
El programa se deja preparado con estas configuraciones, por lo cual dentro de cada directorio relativo a cada pin:
- Se deben guardar las imágenes resultantes y en el formato `png`.
- Se deben guardar todas las transformaciones intermedias del pipeline en la carpeta `DEBUG` y en el formato `png`.
- Se deben copiar el fichero `JSON` de entrada y salida del Analizador.

### Ejecución de la simulación
Una vez que se cumplen los requisitos previos a la simulación, se deben seguir los siguientes pasos:
### Paso 1. Ejecución del programa de análisis de imágenes
Se debe abrir una consola de comandos CMD y navegar hasta el directorio donde se encuentra el programa, según se haya guardado en el equipo y se debe llegar hasta este directorio.
~~~
TFE/
├── Programs/
│   ├── AnalizadorFactory/
~~~
Una vez aquí, se debe activar el entorno virtual `TFG` generado previamente.
~~~
conda activate TFG
~~~
Y ejecutar el programa principal
~~~
python main.py
~~~
### Paso 2. Ejecución del programa de grabación de resultados
Este paso solo procede si se ha decidido realizar la simulación con la BBDD. Previamente se han tenido que crear las tablas e insertar los datos de configuración, tal y como se indica previamente.
Se debe abrir otra consola de comandos CMD y navegar hasta el directorio donde se encuentra el programa, según se haya guardado en el equipo y se debe llegar hasta este directorio.
~~~
TFE/
├── Programs/
│   ├── Resultados/
~~~
Una vez aquí, se debe activar el entorno virtual `TFG` generado previamente.
~~~
conda activate TFG
~~~
Y ejecutar el programa principal
~~~
python main.py
~~~
### Resultado esperado


