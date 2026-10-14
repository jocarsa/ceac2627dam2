import os

ruta = "/var/www/html/ceac2627dam2"

print(os.path.basename(ruta) + "/")

for carpeta, carpetas, archivos in os.walk(ruta):
    carpetas.sort()
    archivos.sort()

    nivel = carpeta.replace(ruta, "").count(os.sep)
    prefijo = "│   " * nivel

    elementos = [(nombre, True) for nombre in carpetas]
    elementos += [(nombre, False) for nombre in archivos]

    for i, (nombre, es_carpeta) in enumerate(elementos):
        esquina = "└── " if i == len(elementos) - 1 else "├── "
        print(prefijo + esquina + nombre + ("/" if es_carpeta else ""))