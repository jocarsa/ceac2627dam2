archivo = open("cursojava.txt",'r')

lineas = archivo.readlines()

for linea in lineas:
  palabras = linea.split(" ")
  for palabra in palabras:
    print(palabra)
    
archivo.close()