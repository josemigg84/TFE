# Usar entorno etiquetado

import os
import subprocess

# Ruta de la carpeta donde están los JSON creados con labelme
directorio = "C:\TFG_Git\Programs\scripts\labelme"

# Recorre todos los archivos en el directorio
for archivo in os.listdir(directorio):
    if archivo.endswith(".json"):
        ruta_json = os.path.join(directorio, archivo)
        nombre = os.path.splitext(archivo)[0]  # nombre sin extensión
        
        print(f"Procesando: {archivo}")
        
        # Ejecuta el comando labelme_json_to_dataset desde un proceso externo
        subprocess.run(["labelme_json_to_dataset", ruta_json], check=True)

print("Todos los JSON han sido procesados.")
