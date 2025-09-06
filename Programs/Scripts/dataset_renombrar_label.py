# Usar entorno etiquetado

from pathlib import Path
import shutil

# Ruta donde están las carpetas creadas al ejecutar el script de labelme
base_dir = Path(r"C:\TFG_Git\Programs\scripts\labelme")
# Ruta de salida para la copia de las máscaras
dest_dir = base_dir / "masks"

# Si no existe la ruta, se crea
dest_dir.mkdir(exist_ok=True)

# Buscar todas las carpetas que terminan en "_json"
for carpeta in base_dir.glob("*_json"):
    if not carpeta.is_dir():
        continue

    numero = carpeta.stem.split("_")[0]  # coge el número del nombre de la carpeta antes de "_json"
    origen = carpeta / "label.png"
    destino = dest_dir / f"{numero}.png"

    if not origen.exists():
        print(f"Fallo: no existe {origen}.")
        continue

    try:
        shutil.copy2(origen, destino)
        print(f"Copiado: {origen} -> {destino}")
    except OSError as e:
        print(f"Fallo: no se pudo copiar {origen}: {e}")

print("Copiados y renombrados todos los label.png")

