import time
import os
import datetime
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from glob import glob

start = time.time()

# Configuración
IMAGE_SIZE = (256, 256)     # recorte de la imagen
BATCH_SIZE = 8              # tamaño del lote
EPOCHS = 20             # número de épocas

image_dir = "augmented_dataset/images"  # directorio de las imagenes
mask_dir = "augmented_dataset/masks"   # directorio de las máscaras

# Función de carga
def cargar_datos(image_dir, mask_dir, image_size):
    image_paths = sorted(glob(os.path.join(image_dir, "*.png")))    # ordenar imágenes por nombre (ya tenian un número aleatorio)
    mask_paths = sorted(glob(os.path.join(mask_dir, "*.png")))   # ordenar máscaras por nombre (ya tenian un número aleatorio)

    images, masks = [], []

    for img_path, msk_path in zip(image_paths, mask_paths):
        img = cv2.imread(img_path)          # leer la imagen
        img = cv2.resize(img, image_size)   # redimensionar, pero ya son de 256x256
        img = img / 255.0                   # normalizar [0-1] cada canal BGR

        msk = cv2.imread(msk_path, cv2.IMREAD_GRAYSCALE)  # leer la máscara en escala de grises
        msk = cv2.resize(msk, image_size)    # redimensionar, pero ya son de 256x256
        msk = (msk > 0).astype(np.float32)     # convierte los píxeles >0 a True (masilla) y el resto a False (fondo)
        msk = np.expand_dims(msk, axis=-1)     # expandir un canal

        images.append(img)
        masks.append(msk)

    return np.array(images), np.array(masks)

# Cargar datos
X, Y = cargar_datos(image_dir, mask_dir, IMAGE_SIZE)

# Modelo U-Net
def crear_modelo(input_shape):
    inputs = layers.Input(shape=input_shape)

    # Encoder
    # Primer bloque convolucional 3x3 con 64 filtros, activación relu y reducir tamaño con MaxPooling
    c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D()(c1)

    # Segundo bloque convolucional 3x3 con 128 filtros, activación relu y reducir tamaño con MaxPooling
    c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D()(c2)

    # Tercer bloque convolucional 3x3 con 256 filtros, activación relu y reducir tamaño con MaxPooling
    c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(p2)
    c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(c3)
    p3 = layers.MaxPooling2D()(c3)

    # Bottleneck, parte más profunda con 512 filtros
    c4 = layers.Conv2D(512, 3, activation='relu', padding='same')(p3)
    c4 = layers.Conv2D(512, 3, activation='relu', padding='same')(c4)

    # Decoder
    # Primer bloque de desconvolución con 256 filtros, aumenta tamaño con Conv2DTranspose, concatena conexiones de tipo 'skip'
    u5 = layers.Conv2DTranspose(256, 2, strides=2, padding='same')(c4)
    u5 = layers.concatenate([u5, c3])
    c5 = layers.Conv2D(256, 3, activation='relu', padding='same')(u5)
    c5 = layers.Conv2D(256, 3, activation='relu', padding='same')(c5)

    # Segundo bloque de desconvolución con 128 filtros, aumenta tamaño con Conv2DTranspose, concatena conexiones de tipo 'skip'
    u6 = layers.Conv2DTranspose(128, 2, strides=2, padding='same')(c5)
    u6 = layers.concatenate([u6, c2])
    c6 = layers.Conv2D(128, 3, activation='relu', padding='same')(u6)
    c6 = layers.Conv2D(128, 3, activation='relu', padding='same')(c6)

    # Tercer bloque de desconvolución con 64 filtros, aumenta tamaño con Conv2DTranspose, concatena conexiones de tipo 'skip'
    u7 = layers.Conv2DTranspose(64, 2, strides=2, padding='same')(c6)
    u7 = layers.concatenate([u7, c1])
    c7 = layers.Conv2D(64, 3, activation='relu', padding='same')(u7)
    c7 = layers.Conv2D(64, 3, activation='relu', padding='same')(c7)

    # Capa final con 1 filtro y activación sigmoide. Devuelve probabilidad por pixel de pertenecer a la clase (segmentación semántica binaria)
    outputs = layers.Conv2D(1, 1, activation='sigmoid')(c7)

    # Devuelve el modelo
    return models.Model(inputs, outputs)

binary_iou = tf.keras.metrics.BinaryIoU(name="IoU", threshold=0.5)  # si se predice probabilidad >= 0.50 clase 1 (masilla), <0.50 clase 0 (fondo)

# TensorBoard con logs para gráficas
logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_cb = TensorBoard(log_dir=logdir, histogram_freq=0)

# Guardar el mejor modelo según IoU de validación
guardar_mejor_modelo_IoU_cb = ModelCheckpoint(
    "unet_model5_8010.keras",
    monitor="val_IoU",
    mode="max",
    save_best_only=True
)

# Crear modelo y compilar
model = crear_modelo(input_shape=(*IMAGE_SIZE, 3))
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy', binary_iou]
)
# Entrenar el modelo
model.fit(
    X, Y,
    batch_size=BATCH_SIZE, # tamaño del lote
    epochs=EPOCHS,      # número de épocas
    validation_split=0.2,       # Se usa un 20% del conjunto de datos para validación
    callbacks=[guardar_mejor_modelo_IoU_cb, tensorboard_cb],
    verbose=1   #mostrar la barra de progreso de cada lote dentro de cada época
)

# mostrar el tiempo total de entrenamiento en segundos
end = time.time()
print(f"Tiempo total: {end - start:.2f} segundos")

