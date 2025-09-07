import json
import os

# Nombre del fichero JSON en el mismo directorio
json_file = "cordon.json"

# Leer JSON
with open(json_file, "r") as f:
    data = json.load(f)

# Extraer los puntos
puntos = data["shapes"][0]["points"]

# Redondear los valores de los puntos y pasarlos a tuplas (x, y)
puntos_redondeados = [(round(x), round(y)) for x, y in puntos]

# fichero de salida puntos.txt en el mismo directorio
fichero_salida = os.path.join(os.path.dirname(json_file), "puntos.txt")

# Escribir en el archivo
with open(fichero_salida, "w") as f:
    f.write(str(puntos_redondeados))

print(f"Puntos guardados en {fichero_salida}")
