import psutil

cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory().percent

print("CPU:", cpu, "%")
print("RAM:", ram, "%")