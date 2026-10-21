frase = "Los alumnos de DAM aprenden programación"
  
palabras = frase.split(" ")
for i in range(0,len(palabras)):
  print("la palabra es: ",palabras[i])
  print("la palabra anterior es",palabras[i-1])
  print("la palabra posterior es",palabras[i+1])
  print("-"*30)