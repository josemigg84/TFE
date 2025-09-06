# Usar entorno Data_Augmentation

import cv2
import os

# ajustar path de entrada y salida, y 
PATH_RECORTE_INTPUT = "images/entrenamiento/c1m1"
PATH_RECORTE_OUTPUT = "images/recortes/c1m1"

# ajustar el modelo de imágenes a recortar: c1m1 (cámara 1 modelo 1), c1m2, c2m1, c2m2
MODELO = "c1m1"

# ajustar el número de la imagen para inicio
# colocar el siguiente número de imagen, según las realizadas ya en la carpeta de recortes
inicio = 1  


TAMANO_RECORTE = (256, 256)  
puntos_recortes_analisis = {
    "c1m1": [(750, 358), (509, 448), (457, 692), (450, 934), (938, 570), (1154, 787), (1394, 786), (1632, 790), (692, 762), (1223, 1172), (700, 586), (928, 779), (954, 1016), (1184, 1017)],
    "c2m1": [(1565, 387), (1321, 316), (1639, 628), (1518, 780), (1818, 432), (1043, 774), (801, 774), (572, 770), (369, 767), (902, 1184), (363, 1050), (628, 1061), (1279, 605), (1277, 771)],
    "c1m2": [(912, 350), (189, 230), (430, 302), (670, 403), (604, 645), (659, 889), (650, 1125), (889, 837), (1133, 807), (1368, 804), (1599, 762), (1837, 749), (1500, 1169), (841, 626), (1041, 591), (1287, 1040)],
    "c2m2": [(1141, 314), (1372, 361), (1597, 289), (1827, 254), (1497, 592), (1432, 794), (1411, 1034), (1214, 840), (991, 814), (770, 758), (533, 711), (303, 691), (87, 689), (642,1184 ), (1760, 590), (1713, 887), (1013, 582), (74, 875)]    
  }

#Función para hacer recortes de la imagen, para el entrenamiento
def recortar(imagen, puntos, tamano, path_output, inicio):
    
    ancho, alto = tamano
    
    # Crear carpeta de salida si no existe
    os.makedirs(path_output, exist_ok=True)
    
    contador = 0
    
    # Hacer recortes
    for i, (x, y) in enumerate(puntos):
        recorte = imagen[y:y + alto, x:x + ancho]
        
        # Verificar dimensiones antes de guardar
        if recorte.shape[0] != alto or recorte.shape[1] != ancho:
            print(f"Recorte {i} fuera de límites.")
            continue

        ruta_salida = os.path.join(path_output, f"{contador + inicio}.png")
        cv2.imwrite(ruta_salida, recorte)
        contador += 1
    
    return contador



# PARA RECORTAR IMAGENES DE UNA CARPETA 

print(f"Carpeta de entrada: {PATH_RECORTE_INTPUT}")
print("Archivos encontrados:")
print(os.listdir(PATH_RECORTE_INTPUT))


for filename in os.listdir(PATH_RECORTE_INTPUT):
    if not filename.lower().endswith(".jpg"):
        continue  # ignorar archivos que no sean imágenes

    imagen_path = os.path.join(PATH_RECORTE_INTPUT, filename)
    imagen = cv2.imread(imagen_path)
    print(f"Procesando: {imagen_path}")
    if imagen is None:
        print(f"No se pudo cargar: {imagen_path}")
        continue

    contador_salida = recortar(imagen, puntos_recortes_analisis[MODELO], TAMANO_RECORTE, PATH_RECORTE_OUTPUT, inicio)
    inicio += contador_salida

