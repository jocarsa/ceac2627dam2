#!/usr/bin/env python3
import psutil
from datetime import datetime

hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory().percent

archivo = open("/home/josevicente/Escritorio/registros.csv",'a')
archivo.write(str(hoy)+","+str(cpu)+","+str(ram)+"\n")
archivo.close()