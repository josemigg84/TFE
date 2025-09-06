# Usar entorno Data_Augmentation

import os
import cv2
import random
import albumentations as a

# Configuración de path_in y path_out
input_img_dir = 'dataset/images'
input_msk_dir = 'dataset/masks'

output_img_dir = 'augmented_dataset/images'
output_msk_dir = 'augmented_dataset/masks'

# Guardar también el original junto a las augmentations
SAVE_ORIGINAL = True
OVERWRITE_ORIGINAL = False         # True para sobrescribirlo si ya existe

# Crear carpetas de salida si no existen
os.makedirs(output_img_dir, exist_ok=True)
os.makedirs(output_msk_dir, exist_ok=True)

# Definir augmentations
transform = a.Compose([
    a.HorizontalFlip(p=0.5),
    a.VerticalFlip(p=0.3),
    a.RandomRotate90(p=0.5),
    a.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=15,
                       border_mode=cv2.BORDER_REFLECT, p=0.7),
    a.RandomBrightnessContrast(p=0.3),
],
    additional_targets={'mask': 'mask'}
)

# Obtener archivos por nombre desde input_img_dir
image_files = sorted([f for f in os.listdir(input_img_dir) if f.endswith(".png")])

# Conjunto para guardar nombres ya usados
used_names = set()

# Generar nombre aleatorio de 6 dígitos
def unique_random_name():
    while True:
        name = f"{random.randint(100000, 999999)}.png"
        if name not in used_names:
            used_names.add(name)
            return name

# Aplicar augmentations y guardar
num_aug = 29  # cuántas versiones aumentadas por imagen

for file_name in image_files:
    img_path = os.path.join(input_img_dir, file_name)
    msk_path = os.path.join(input_msk_dir, file_name)  # la máscara debe tener el mismo nombre que la imagen

    if not os.path.exists(msk_path):
        print(f"FALLO: no existe máscara para {file_name}")
        continue

    image = cv2.imread(img_path)
    mask = cv2.imread(msk_path, cv2.IMREAD_GRAYSCALE)

    # Guardar el original (opcional)
    if SAVE_ORIGINAL:
        nombre_aleatorio = unique_random_name()
        img_salida = os.path.join(output_img_dir, nombre_aleatorio)
        msk_salida = os.path.join(output_msk_dir, nombre_aleatorio)

        if OVERWRITE_ORIGINAL or not (os.path.exists(img_salida) and os.path.exists(msk_salida)):
            cv2.imwrite(img_salida, image)
            cv2.imwrite(msk_salida, mask)

    # Generar y guardar augmentations
    for i in range(num_aug):
        augmented = transform(image=image, mask=mask)
        aug_img = augmented['image']
        aug_msk = augmented['mask']

        nombre_aleatorio = unique_random_name()
        cv2.imwrite(os.path.join(output_img_dir, nombre_aleatorio), aug_img)
        cv2.imwrite(os.path.join(output_msk_dir, nombre_aleatorio), aug_msk)

print("Augmentaciones completadas.")

