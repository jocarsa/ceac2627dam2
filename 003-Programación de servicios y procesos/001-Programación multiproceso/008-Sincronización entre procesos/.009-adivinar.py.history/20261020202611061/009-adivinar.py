
import sqlite3
import re
import random
from collections import defaultdict

BASE_DATOS = "palabras.db"
VENTANA = 10

conexion = sqlite3.connect(BASE_DATOS)
cursor = conexion.cursor()

# ----------------------------------------
# 1. Cargar palabras y frecuencias
# ----------------------------------------

cursor.execute("""
    SELECT id, palabra, frecuencia
    FROM palabras
""")

datos = cursor.fetchall()

palabras_por_id = {}
ids_por_palabra = {}
frecuencias = {}

for identificador, palabra, frecuencia in datos:
    palabras_por_id[identificador] = palabra
    ids_por_palabra[palabra] = identificador
    frecuencias[palabra] = frecuencia

print("Vocabulario cargado:", len(datos), "palabras")

# ----------------------------------------
# 2. Cargar relaciones posteriores
# ----------------------------------------

cursor.execute("""
    SELECT
        palabra_id,
        relacionada_id,
        distancia,
        frecuencia
    FROM relaciones
    WHERE direccion = 'posterior'
""")

relaciones = defaultdict(list)

for origen, destino, distancia, frecuencia in cursor.fetchall():

    relaciones[origen].append((
        destino,
        distancia,
        frecuencia
    ))

print("Relaciones cargadas")

# ----------------------------------------
# 3. Predecir siguiente palabra
# ----------------------------------------

def predecir(texto):

    palabras = re.findall(
        r"\b\w+\b",
        texto.lower(),
        flags=re.UNICODE
    )

    contexto = palabras[-VENTANA:]

    puntuaciones = defaultdict(float)

    # Analizar cada palabra del contexto
    for posicion, palabra in enumerate(reversed(contexto)):

        if palabra not in ids_por_palabra:
            continue

        palabra_id = ids_por_palabra[palabra]

        # Distancia de la palabra respecto
        # a la posición que queremos predecir
        distancia_esperada = posicion + 1

        for destino, distancia, frecuencia in relaciones[palabra_id]:

            # Solo relaciones con distancia correcta
            if distancia != distancia_esperada:
                continue

            candidata = palabras_por_id[destino]

            # Dar mayor peso a palabras cercanas
            peso = 1 / distancia_esperada

            puntuaciones[candidata] += frecuencia * peso

    # Si no encontramos relaciones,
    # utilizar palabras frecuentes
    if not puntuaciones:

        for palabra, frecuencia in frecuencias.items():
            puntuaciones[palabra] = frecuencia

    # Elegir la mejor candidata
    mejor = max(
        puntuaciones,
        key=puntuaciones.get
    )

    return mejor


# ----------------------------------------
# 4. Programa interactivo
# ----------------------------------------

print("\nPREDICTOR DE TEXTO")
print("------------------------------")
print("Escribe cinco palabras iniciales.")
print("Pulsa ENTER para generar una nueva.")
print("Escribe 'salir' para terminar.\n")

texto = input("Texto inicial: ").strip()

while True:

    print("\n" + texto)

    entrada = input("\nENTER = siguiente palabra | salir: ")

    if entrada.lower().strip() == "salir":
        break

    nueva_palabra = predecir(texto)

    texto += " " + nueva_palabra

conexion.close()

print("\nTexto generado:")
print(texto)
