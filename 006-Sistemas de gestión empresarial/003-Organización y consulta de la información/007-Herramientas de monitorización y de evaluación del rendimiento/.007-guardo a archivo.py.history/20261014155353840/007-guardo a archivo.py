import psutil

cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory().percent

archivo = open("registros.csv")
archivo.write(cpu+","+ram+","+)