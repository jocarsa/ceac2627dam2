
import sqlite3
import re
import random
from collections import Counter, defaultdict

BASE_DATOS = "palabras.db"
VENTANA = 10

# ----------------------------------------
# 1. Conectar a SQLite
# ----------------------------------------

conexion = sqlite3.connect(BASE_DATOS)
cursor = conexion.cursor()

# ----------------------------------------
# 2. Reconstruir secuencia original
# ----------------------------------------

cursor.execute("""
    SELECT
        p.palabra
    FROM contextos c
    JOIN palabras p ON c.palabra_id = p.id
    ORDER BY c.posicion
""")

corpus = [fila[0] for fila in cursor.fetchall()]

print("Palabras cargadas:", len(corpus))

if not corpus:
    raise SystemExit("La base de datos no contiene contextos.")

# ----------------------------------------
# 3. Construir modelo de n-gramas
# ----------------------------------------

print("Construyendo modelo...")

modelo = {
    n: defaultdict(Counter)
    for n in range(1, VENTANA + 1)
}

frecuencias = Counter(corpus)

for i in range(1, len(corpus)):

    siguiente = corpus[i]

    for n in range(1, min(VENTANA, i) + 1):

        contexto = tuple(corpus[i-n:i])

        modelo[n][contexto][siguiente] += 1

print("Modelo preparado.")

# ----------------------------------------
# 4. Detectar repeticiones
# ----------------------------------------

def repeticion(texto, candidata):

    # Evitar ciclos inmediatos de 1 a 5 palabras
    secuencia = texto + [candidata]

    for longitud in range(1, 6):

        if len(secuencia) < longitud * 2:
            continue

        ultimo = secuencia[-longitud:]
        anterior = secuencia[-2*longitud:-longitud]

        if ultimo == anterior:
            return True

    return False

# ----------------------------------------
# 5. Elegir siguiente palabra
# ----------------------------------------

def predecir(texto):

    palabras = re.findall(
        r"\b\w+\b",
        texto.lower(),
        flags=re.UNICODE
    )

    # Solo las últimas 10 palabras
    contexto = palabras[-VENTANA:]

    # Buscar coincidencias desde 10 hasta 1
    for n in range(min(VENTANA, len(contexto)), 0, -1):

        clave = tuple(contexto[-n:])

        if clave not in modelo[n]:
            continue

        candidatos = modelo[n][clave]

        opciones = []
        pesos = []

        for palabra, frecuencia in candidatos.items():

            if repeticion(palabras, palabra):
                continue

            # Penalizar palabras muy repetidas
            recientes = palabras[-20:]
            veces = recientes.count(palabra)

            penalizacion = 1 / (1 + veces * 2)

            peso = frecuencia * penalizacion

            opciones.append(palabra)
            pesos.append(peso)

        if opciones:

            return random.choices(
                opciones,
                weights=pesos,
                k=1
            )[0]

    # Fallback: palabra frecuente sin repetición
    opciones = []
    pesos = []

    for palabra, frecuencia in frecuencias.items():

        if repeticion(palabras, palabra):
            continue

        veces = palabras[-20:].count(palabra)

        opciones.append(palabra)
        pesos.append(frecuencia / (1 + veces * 2))

    return random.choices(
        opciones,
        weights=pesos,
        k=1
    )[0]


# ----------------------------------------
# 6. Interfaz interactiva
# ----------------------------------------

print("\nPREDICTOR CONTEXTUAL")
print("--------------------------------")
print("Escribe cinco palabras.")
print("ENTER: generar siguiente palabra.")
print("salir: terminar.\n")

texto = input("Texto inicial: ").strip()

while True:

    print("\n" + texto)

    entrada = input(
        "\nENTER = siguiente palabra | salir: "
    )

    if entrada.lower().strip() == "salir":
        break

    nueva = predecir(texto)

    texto += " " + nueva

    print("\nPredicción:", nueva)

conexion.close()

print("\nTEXTO FINAL:")
print(texto)
