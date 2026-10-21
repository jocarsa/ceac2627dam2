archivo = open("cursojava.txt",'r')

lineas = archivo.readlines()

for linea in lineas:
  palabras = linea.split(" ")
  print("Cuantas palabras tengo?")
  print("tengo: ",len(palabras))
    
archivo.close()