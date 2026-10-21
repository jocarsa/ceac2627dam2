archivo = open("lemario.txt",'r')

lineas = archivo.readlines()

for linea in lineas:
  print(linea)
  
archivo.close()