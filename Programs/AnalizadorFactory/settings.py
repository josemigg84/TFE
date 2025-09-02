import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "models", "unet_model4_8010.keras")
QUEUE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),"data","App","Local","ordenes","fifo_grabar_analizar")      #ruta absoluta al directorio de la cola fifo, para ruta relativa utilizar -> os.getcwd()
QUEUE_DIR_FALLOS = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),"data","App","Local","ordenes","fifo_grabar_analizar_fallos")  #ruta absoluta al directorio de errores de la cola fifo
PATH_GUARDAR_JSON = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),"data","App","Local","ordenes","fifo_analizar_resultados") # ir a dos carpetas anteriores del directorio actual (quitar: programs/Analizador) y añadirle: temp/App/Local/Data/orders/analyzed/
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "logs")
IMAGEN_DEBUG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "debug")         #path donde se guardan las imagenes intermedias
IMAGEN_GUARDAR = True               #OPCION DE GUARDAR O NO LAS IMAGENES RESULTANTES, POR ESPACIO
IMAGEN_DEBUG = True                 #OPCION DE GUARDAR TODAS LAS TRANSFORMACIONES DE IMAGENES. Cada vez que se ejecuta se sobreescriben
COPIA_JSON_IN_OUT = True            #Opción que copia el json de entrada y de salida en la carpeta de resultados de imagen
DIBUJAR_VENTANAS_RECORTE = True    #OPCION DE DIBUJAR EN LA IMAGEN LAS VENTANAS QUE SE RECORTAN PARA LA FCN
DIBUJAR_CORDONES_ORIGINALES = False  # == True dibuja en la imagen los cordones orginales y los modificados; ==False solo dibuja los cordones modificados
FORMATO_GUARDAR_RES = "png" #png o jpg
FORMATO_GUARDAR_DEBUG = "png"
FORMATO_GUARDAR_MASK = "png"
ANCHO_IMAGEN = 2560
ALTO_IMAGEN = 1440
TAMANO_RECORTE = (256, 256)        # NO SE PUEDE MODIFICAR PORQUE EL MODELO ESTÁ ENTRENADO ASÍ, ancho y alto del recorte
UMBRAL_RES_POSICION = 0.60              # por defecto, se puede cambiar en cada llamada, para resultado de metodo posicion
UMBRAL_BIN_POSICION = 80                # por defecto, se puede cambiar en cada llamada, para binarizar imagen en el metodo posicion
UMBRAL_RES_ANGULO = 2             # por defecto, se puede cambiar en cada llamada, para resultado de metodo angulo
UMBRAL_BIN_ANGULO = 80                # por defecto, se puede cambiar en cada llamada, para binarizar imagen en el metodo angulo
MAX_REINTENTOS = 3
COLOR_NEGRO = (0, 0, 0)
COLOR_VERDE = (0, 255, 0)
COLOR_ROJO = (0, 0, 255)
COLOR_AZUL = (255, 255, 0)
COLOR_MORADO = (255, 0, 255)
COLOR_VENTANA = (199, 67, 117)
COLOR_CORDON = (255, 0, 0)
COLOR_AMARILLO = (0, 255, 255)

MODELOS = {
    13: 1,
    14: 1,
    23: 2,
    24: 2
}

CONFIGURACIONES = {
    "camara1": {
        "1": {  #Modelo
            "cfg_ini": {                                            # son de la imagen de referencia 6000000
                'ROI_POS_INI': (1265, 890, 240, 189),                # region de interes para posición: roi_x, roi_y, ancho, alto. (Es fija e inicial, desde donde parte)
                'ROI_ANG_INI': (240, 579, 230, 939, 50, 1),          # region de interes para ángulo: roi_x1, roi_y1, roi_x2, roi_y2, ancho, alto.
                'POSICION_INI': (1385, 988),                         # valor del centro de patrón en la imagen de referencia
                'ANGULO_INI': -1.4320961841646493,                   # valor de la rotación en grados de la ventana en la imagen de referencia
                'MARGEN_PIXELES_CORDONES': [4, 4, 2]              # margen de píxeles de masilla alrededor de cada punto del cordón para que el resultado sea bueno. cordones 1, 2, y 3.  Configurable por cordon, cámara y modelo
            },
            "cordones": {
                "cordon1": [(923, 469), (879, 474), (831, 480), (786, 486), (743, 492), (713, 497), (697, 509), (687, 526), (674, 549), (659, 564), (636, 575), (607, 585), (586, 605), (574, 633), (572, 668), (572, 703), (569, 738), (568, 781), (570, 824), (578, 858), (594, 881), (614, 898), (635, 909), (657, 920), (681, 922), (710, 922), (731, 923), (767, 923), (807, 920), (844, 918), (881, 917), (922, 915), (959, 916), (998, 916), (1038, 916), (1075, 916), (1112, 917), (1147, 916), (1184, 914), (1221, 913), (1262, 913), (1301, 912), (1343, 910), (1385, 905), (1427, 906), (1476, 906), (1520, 905), (1567, 905), (1612, 906), (1657, 907), (1698, 908), (1742, 908), (1772, 906), (1796, 907)],
                "cordon2": [(661, 920), (662, 944), (662, 967), (652, 979), (628, 982), (599, 983), (583, 997), (574, 1023), (576, 1056), (576, 1093), (573, 1119), (563, 1132), (551, 1140)],
                "cordon3": [(1313, 1305), (1337, 1303), (1360, 1300), (1381, 1298), (1393, 1296)]
            },
            "puntos_entrenamiento": [(750, 358), (509, 448), (457, 692), (450, 934), (938, 570), (1154, 787), (1394, 786), (1632, 790), (692, 762), (1223, 1172), (700, 586), (928, 779), (954, 1016), (1184, 1017)],
            "puntos_recortes_analisis": [(750, 358), (509, 448), (457, 692), (450, 934), (1154, 787), (1394, 786), (1632, 790), (692, 762), (1223, 1172), (928, 779)],
            "path_patron": os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "patrones", "patron_c1_m1.jpg"),
            "segmentos": {
                "limite_sin_masilla_matriz": 2,
                "min_malos_seguidos": 10,
                "min_buenos_seguidos": 6,
                "precision_decimales_normalizar": 6
            }
        },
        "2": {  #Modelo
            "cfg_ini": {                                             # son de la imagen de referencia 6000001
                'ROI_POS_INI': (1640, 925, 240, 189),
                'ROI_POS_INI_2': (885, 350, 115, 115),
                'ROI_ANG_INI': (375, 716, 375, 920, 50, 1),
                'POSICION_INI': (1759, 1014),
                'POSICION_INI_2': (942, 409),
                'ANGULO_INI': -0.8425242607404186,
                'MARGEN_PIXELES_CORDONES': [4, 4, 4, 2]              # margen de pixeles de masilla alrededor de cada punto del cordón para que el resultado sea bueno. cordones 1, 2, 3 y 4. Configurable por cordon, cámara y modelo
            },
            "cordones": {
                "cordon1": [(325, 383), (348, 385), (380, 387), (407, 389), (432, 390), (469, 390), (499, 390), (527, 389), (545, 390), (561, 392), (574, 396), (582, 404), (590, 414), (595, 422), (603, 430), (609, 436), (616, 440), (623, 445), (635, 447), (646, 449), (658, 451), (669, 452), (680, 453), (692, 455), (704, 457), (715, 458), (724, 461), (734, 464), (745, 469), (755, 476), (763, 484), (774, 494), (780, 505), (785, 517), (790, 529), (796, 545), (803, 561), (807, 574), (814, 592)],
                "cordon2": [(1096, 469), (1078, 488), (1059, 505), (1035, 515), (1002, 527), (969, 533), (932, 542), (886, 551), (839, 558), (797, 564), (772, 570), (759, 578), (751, 588), (747, 600), (742, 620), (737, 639), (733, 663), (730, 687), (729, 714), (730, 748), (732, 780), (733, 809), (733, 834), (733, 863), (730, 886), (726, 914), (726, 936), (733, 950), (744, 959), (762, 962), (785, 959), (808, 957), (831, 955), (856, 953), (883, 951), (912, 949), (942, 947), (972, 945), (1004, 943), (1038, 941), (1073, 939), (1109, 938), (1145, 937), (1179, 934), (1216, 931), (1257, 923), (1300, 914), (1337, 906), (1375, 904), (1413, 902), (1450, 902), (1492, 902), (1532, 905), (1577, 905), (1613, 899), (1655, 894), (1695, 892), (1734, 889), (1778, 888), (1819, 889), (1865, 887), (1909, 888), (1948, 888), (1990, 888), (2029, 886), (2043, 887)],
                "cordon3": [(797, 957), (798, 995), (799, 1028), (799, 1060), (799, 1090), (799, 1125), (799, 1163), (799, 1192), (796, 1217), (779, 1221), (757, 1223), (744, 1224), (736, 1224)],
                "cordon4": [(1552, 1330), (1576, 1331), (1598, 1329), (1619, 1327), (1642, 1325), (1666, 1321), (1688, 1318)]
            },
            "puntos_entrenamiento": [(912, 350), (189, 230), (430, 302), (670, 403), (604, 645), (659, 889), (650, 1125), (889, 837), (1133, 807), (1368, 804), (1599, 762), (1837, 749), (1500, 1169), (841, 626), (1041, 591), (1287, 1040)],
            "puntos_recortes_analisis": [(912, 350), (189, 230), (430, 302), (670, 403), (604, 645), (659, 889), (650, 1125), (889, 837), (1133, 807), (1368, 804), (1599, 762), (1837, 749), (1500, 1169)],
            "path_patron": os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "patrones", "patron_c1_m2.jpg"),
            "path_patron_2": os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "patrones", "patron2_c1_m2.jpg"),
            "segmentos": {
                "limite_sin_masilla_matriz": 2,
                "min_malos_seguidos": 10,
                "min_buenos_seguidos": 6,
                "precision_decimales_normalizar": 6
            }
        }
    },
    "camara2": {
        "1": {  #Modelo
            "cfg_ini": {                                             # son de la imagen de referencia 6000002
                'ROI_POS_INI': (1081, 921, 165, 200),
                'ROI_ANG_INI': (705, 1012, 995, 1024, 1, 50),
                'POSICION_INI': (1163, 1012),
                'ANGULO_INI': -2.96093613416375,
                'MARGEN_PIXELES_CORDONES': [4, 4, 2]              # margen de píxeles de masilla alrededor de cada punto del cordón para que el resultado sea bueno. cordones 1, 2, y 3.  Configurable por cordon, cámara y modelo
            },
            "cordones": {
                "cordon1": [(1403, 428), (1427, 433), (1452, 439), (1476, 446), (1499, 451), (1518, 455), (1541, 457), (1568, 459), (1589, 461), (1608, 462), (1622, 471), (1631, 486), (1638, 501), (1652, 516), (1669, 531), (1684, 541), (1696, 553), (1713, 565), (1726, 580), (1738, 599), (1750, 622), (1752, 650), (1753, 679), (1753, 714), (1753, 747), (1752, 782), (1752, 811), (1747, 831), (1739, 848), (1729, 862), (1717, 874), (1705, 883), (1692, 888), (1676, 892), (1662, 896), (1643, 899), (1621, 901), (1598, 903), (1572, 904), (1546, 905), (1514, 905), (1481, 904), (1446, 903), (1407, 902), (1369, 901), (1331, 901), (1295, 899), (1256, 896), (1215, 895), (1176, 892), (1135, 892), (1097, 890), (1058, 889), (1022, 890), (984, 890), (952, 890), (915, 889), (879, 890), (847, 889), (815, 888), (787, 887), (759, 885), (732, 883), (705, 883), (672, 881), (641, 880), (614, 878), (582, 876), (552, 874), (530, 872), (508, 870), (484, 870), (465, 874), (453, 871)],
                "cordon2": [(1858, 726), (1830, 728), (1797, 733), (1768, 741), (1756, 765), (1752, 796), (1750, 809)],
                "cordon3": [(982, 1305), (1000, 1307), (1018, 1309), (1037, 1312), (1054, 1313), (1068, 1314)]
            },
            "puntos_entrenamiento": [(1565, 387), (1321, 316), (1639, 628), (1518, 780), (1818, 432), (1043, 774), (801, 774), (572, 770), (369, 767), (902, 1184), (363, 1050), (628, 1061), (1279, 605), (1277, 771)],
            "puntos_recortes_analisis": [(1565, 387), (1321, 316), (1665, 628), (1518, 780), (1043, 774), (801, 774), (572, 770), (369, 767), (902, 1184), (1277, 771)],
            "path_patron": os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "patrones", "patron_c2_m1.jpg"),
            "segmentos": {
                "limite_sin_masilla_matriz": 2,
                "min_malos_seguidos": 10,
                "min_buenos_seguidos": 6,
                "precision_decimales_normalizar": 6
            }
        },
        "2": {  #Modelo
            "cfg_ini": {                                             # son de la imagen de referencia 6000003
                'ROI_POS_INI': (464, 869, 490, 210),
                'ROI_POS_INI_2': (1324, 315, 115, 115),
                'ROI_ANG_INI': (557, 992, 840, 1004, 1, 50),
                'POSICION_INI': (714, 969),
                'POSICION_INI_2': (1381, 368),
                'ANGULO_INI': -3.2358925085412387,
                'MARGEN_PIXELES_CORDONES': [4, 4, 4, 2]              # margen de píxeles de masilla alrededor de cada punto del cordón para que el resultado sea bueno. cordones 1, 2, 3 y 4. Configurable por cordon, cámara y modelo
            },
            "cordones": {
                "cordon1": [(2030, 370), (2005, 368), (1979, 368), (1952, 368), (1933, 368), (1905, 366), (1875, 364), (1843, 362), (1809, 360), (1782, 360), (1763, 368), (1751, 379), (1743, 392), (1738, 407), (1733, 416), (1715, 417), (1695, 420), (1675, 422), (1651, 423), (1630, 425), (1606, 429), (1579, 436), (1564, 445), (1555, 456), (1547, 473), (1538, 492), (1530, 503), (1523, 517), (1514, 528)],
                "cordon2": [(1223, 422), (1235, 435), (1249, 445), (1264, 458), (1279, 467), (1297, 477), (1313, 485), (1333, 491), (1354, 496), (1378, 503), (1404, 508), (1432, 512), (1457, 518), (1488, 522), (1513, 527), (1542, 535), (1567, 550), (1577, 570), (1585, 590), (1585, 605), (1585, 627), (1583, 653), (1581, 684), (1580, 717), (1578, 756), (1576, 793), (1576, 829), (1576, 857), (1576, 881), (1571, 900), (1561, 913), (1542, 923), (1527, 928), (1503, 929), (1478, 930), (1450, 931), (1415, 932), (1375, 931), (1337, 929), (1300, 929), (1264, 926), (1224, 923), (1186, 918), (1152, 914), (1116, 910), (1074, 904), (1036, 898), (1000, 890), (960, 878), (925, 868), (889, 858), (850, 853), (819, 850), (779, 847), (739, 843), (706, 840), (669, 838), (632, 837), (593, 835), (556, 833), (518, 833), (477, 831), (435, 830), (396, 829), (351, 829), (315, 828), (268, 826), (232, 826), (197, 826), (171, 826), (154, 825)],
                "cordon3": [(1505, 929), (1505, 962), (1504, 987), (1503, 1015), (1504, 1045), (1500, 1060), (1489, 1068), (1474, 1079), (1460, 1090), (1453, 1105), (1449, 1121), (1447, 1143), (1448, 1168), (1452, 1196), (1459, 1219), (1476, 1234), (1503, 1235), (1524, 1233), (1547, 1227), (1560, 1215)],
                "cordon4": [(720, 1330), (746, 1337), (773, 1344), (800, 1350), (810, 1350)]
            },
            "puntos_entrenamiento": [(1141, 314), (1372, 361), (1597, 289), (1827, 254), (1497, 592), (1432, 794), (1411, 1034), (1214, 840), (991, 814), (770, 758), (533, 711), (303, 691), (87, 689), (642,1184 ), (1760, 590), (1713, 887), (1013, 582), (74, 875)],
            "puntos_recortes_analisis": [(1141, 314), (1372, 361), (1597, 289), (1827, 254), (1447, 592), (1432, 794), (1380, 1034), (1214, 840), (991, 814), (770, 758), (533, 711), (303, 691), (87, 689), (642, 1184)],
            "path_patron": os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "patrones", "patron_c2_m2.jpg"),
            "path_patron_2": os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "patrones", "patron2_c2_m2.jpg"),
            "segmentos": {
                "limite_sin_masilla_matriz": 2,
                "min_malos_seguidos": 10,
                "min_buenos_seguidos": 6,
                "precision_decimales_normalizar": 6
            }
        }
    }
}




