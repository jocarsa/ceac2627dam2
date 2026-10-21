
archivo = open("cursojava.txt", "r", encoding="utf-8")

texto = archivo.read().lower()
archivo.close()

# Convertimos el texto en una lista de palabras
palabras = texto.split()

# Creamos un conjunto de palabras únicas
unicas = set(palabras)

print("Total de palabras:", len(palabras))
print("Palabras diferentes:", len(unicas))

# Diccionario para contar repeticiones
frecuencias = {}

for palabra in unicas:
    frecuencias[palabra] = palabras.count(palabra)

# Ordenamos de mayor a menor frecuencia
ordenadas = sorted(
    frecuencias.items(),
    key=lambda elemento: elemento[1],
    reverse=True
)

# Mostramos los resultados
print("\nESTADÍSTICA DE PALABRAS")
print("---------------------------")

for palabra, cantidad in ordenadas:
    print(palabra, ":", cantidad)
