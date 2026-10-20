archivo = open("cursojava.txt",'r')

lineas = archivo.readlines()

for linea in lineas:
  palabras = linea.split(" ")
  