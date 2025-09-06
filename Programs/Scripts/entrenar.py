import time
import os
import datetime
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ModelCheckpoint, LambdaCallback, TensorBoard
from glob import glob

start = time.time()

# Configuración
IMAGE_SIZE = (256, 256)
BATCH_SIZE = 16
EPOCHS = 30

image_dir = "augmented_dataset/images"
mask_dir = "augmented_dataset/masks"

# Función de carga
def load_data(image_dir, mask_dir, image_size):
    image_paths = sorted(glob(os.path.join(image_dir, "*.png")))
    mask_paths = sorted(glob(os.path.join(mask_dir, "*.png")))

    images, masks = [], []

    for img_path, msk_path in zip(image_paths, mask_paths):
        img = cv2.imread(img_path)
        img = cv2.resize(img, image_size)
        img = img / 255.0

        msk = cv2.imread(msk_path, cv2.IMREAD_GRAYSCALE)
        msk = cv2.resize(msk, image_size)
        msk = (msk > 0).astype(np.float32)
        msk = np.expand_dims(msk, axis=-1)

        images.append(img)
        masks.append(msk)

    return np.array(images), np.array(masks)

# Cargar datos
X, Y = load_data(image_dir, mask_dir, IMAGE_SIZE)

# Modelo U-Net
def build_unet(input_shape):
    inputs = layers.Input(shape=input_shape)

    # Encoder
    c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D()(c1)

    c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D()(c2)

    c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(p2)
    c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(c3)
    p3 = layers.MaxPooling2D()(c3)

    # Bottleneck
    c4 = layers.Conv2D(512, 3, activation='relu', padding='same')(p3)
    c4 = layers.Conv2D(512, 3, activation='relu', padding='same')(c4)

    # Decoder
    u5 = layers.Conv2DTranspose(256, 2, strides=2, padding='same')(c4)
    u5 = layers.concatenate([u5, c3])
    c5 = layers.Conv2D(256, 3, activation='relu', padding='same')(u5)
    c5 = layers.Conv2D(256, 3, activation='relu', padding='same')(c5)

    u6 = layers.Conv2DTranspose(128, 2, strides=2, padding='same')(c5)
    u6 = layers.concatenate([u6, c2])
    c6 = layers.Conv2D(128, 3, activation='relu', padding='same')(u6)
    c6 = layers.Conv2D(128, 3, activation='relu', padding='same')(c6)

    u7 = layers.Conv2DTranspose(64, 2, strides=2, padding='same')(c6)
    u7 = layers.concatenate([u7, c1])
    c7 = layers.Conv2D(64, 3, activation='relu', padding='same')(u7)
    c7 = layers.Conv2D(64, 3, activation='relu', padding='same')(c7)

    outputs = layers.Conv2D(1, 1, activation='sigmoid')(c7)

    return models.Model(inputs, outputs)


binary_iou = tf.keras.metrics.BinaryIoU(name="IoU", threshold=0.5)

# Callbacks
# TensorBoard
logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_cb = TensorBoard(log_dir=logdir, histogram_freq=0)

# Guardar el mejor modelo según IoU de validación
checkpoint_cb = ModelCheckpoint(
    "unet_model5_8010.keras",
    monitor="val_IoU",
    mode="max",
    save_best_only=True
)

# Progreso en consola con métricas
def _fmt(x):
    try:
        return f"{x:.4f}"
    except Exception:
        return "nan"

progress_cb = LambdaCallback(
    on_epoch_end=lambda epoch, logs: print(
        "\n {pct}% completado - "
        "Loss: {loss} | Val Loss: {val_loss} | "
        "IoU: {iou} | Val IoU: {val_iou}".format(
            pct=int((epoch + 1) / EPOCHS * 100),
            loss=_fmt(logs.get("loss", float("nan"))),
            val_loss=_fmt(logs.get("val_loss", float("nan"))),
            iou=_fmt(logs.get("IoU", float("nan"))),
            val_iou=_fmt(logs.get("val_IoU", float("nan")))
        )
    )
)

# Compilar y entrenar
model = build_unet(input_shape=(*IMAGE_SIZE, 3))
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy', binary_iou]
)

model.fit(
    X, Y,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    validation_split=0.2,
    callbacks=[checkpoint_cb, progress_cb, tensorboard_cb],
    verbose=0  # salida al callback
)

end = time.time()
print(f"Tiempo total: {end - start:.2f} segundos")

