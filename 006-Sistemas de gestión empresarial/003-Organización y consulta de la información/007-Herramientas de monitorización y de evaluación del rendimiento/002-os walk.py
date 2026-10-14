import os

for archivo,carpeta,carpetas in os.walk("/var/www/html/ceac2627dam2"):
  print(archivo)
  print(carpeta)
  print(carpetas)
  
  