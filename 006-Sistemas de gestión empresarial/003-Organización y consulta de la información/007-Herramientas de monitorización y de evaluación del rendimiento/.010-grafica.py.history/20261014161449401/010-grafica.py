#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt
from datetime import datetime

fechas = []
cpus = []
rams = []

# Leer CSV
with open("/home/josevicente/Escritorio/registros.csv", "r") as archivo:
    lector = csv.reader(archivo)

    for fila in lector:
        fechas.append(datetime.strptime(fila[0], "%Y-%m-%d %H:%M:%S"))
        cpus.append(float(fila[1]))
        rams.append(float(fila[2]))

# Gráfica CPU
plt.figure()
plt.plot(fechas, cpus, color="blue")
plt.title("Uso de CPU")
plt.xlabel("Fecha y hora")
plt.ylabel("CPU (%)")
plt.ylim(0, 100)
plt.grid()
plt.gcf().autofmt_xdate()

# Gráfica RAM
plt.figure()
plt.plot(fechas, rams, color="green")
plt.title("Uso de RAM")
plt.xlabel("Fecha y hora")
plt.ylabel("RAM (%)")
plt.ylim(0, 100)
plt.grid()
plt.gcf().autofmt_xdate()

# Mostrar ambas gráficas
plt.show()