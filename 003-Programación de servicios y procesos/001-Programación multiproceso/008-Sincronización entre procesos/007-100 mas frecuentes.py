
archivo = open("cursojava.txt", "r", encoding="utf-8")

texto = archivo.read().lower()
archivo.close()

palabras = texto.split()
unicas = set(palabras)

print("Total de palabras:", len(palabras))
print("Palabras diferentes:", len(unicas))

frecuencias = {}

for palabra in palabras:
    frecuencias[palabra] = frecuencias.get(palabra, 0) + 1

ordenadas = sorted(
    frecuencias.items(),
    key=lambda elemento: elemento[1],
    reverse=True
)

print("\nLAS 100 PALABRAS MÁS FRECUENTES")
print("--------------------------------")

for palabra, cantidad in ordenadas[:100]:
    print(palabra, ":", cantidad)
