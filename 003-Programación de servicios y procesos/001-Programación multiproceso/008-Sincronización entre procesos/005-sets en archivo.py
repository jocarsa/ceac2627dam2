archivo = open("cursojava.txt",'r')

lineas = archivo.readlines()

for linea in lineas:
  palabras = linea.split(" ")
  print("Cuantas palabras tengo?")
  print("tengo: ",len(palabras),"diferentes")
  palabras = set(palabras)	# Lo convierto en un conjunto para quitar duplicados
  palabras = list(palabras)	# Ahora vuelve a ser una lista
  print("tengo: ",len(palabras),"unicas")
    
archivo.close()