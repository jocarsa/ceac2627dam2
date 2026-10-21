
import sqlite3
import re
import random
from pathlib import Path
from collections import Counter, defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CARPETA = Path("/var/www/html/clases/")
BASE_DATOS = "conocimiento.db"

VENTANA = 10
LONGITUD_RESPUESTA = 100
TAMANO_FRAGMENTO = 200
SOLAPAMIENTO = 40
FRAGMENTOS_RELEVANTES = 8

# ----------------------------------------
# 1. Base de datos
# ----------------------------------------

conexion = sqlite3.connect(BASE_DATOS)
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS fragmentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo TEXT,
    contenido TEXT
)
""")

conexion.commit()


# ----------------------------------------
# 2. Tokenización
# ----------------------------------------

def tokenizar(texto):
    return re.findall(
        r"\b\w+\b",
        texto.lower(),
        flags=re.UNICODE
    )


# ----------------------------------------
# 3. Leer documentos de carpeta
# ----------------------------------------

def cargar_documentos():

    cursor.execute("DELETE FROM fragmentos")

    archivos = list(CARPETA.rglob("*.txt"))

    print("Archivos encontrados:", len(archivos))

    total = 0

    for archivo in archivos:

        try:
            texto = archivo.read_text(
                encoding="utf-8"
            )
        except UnicodeError:
            print("No se pudo leer:", archivo)
            continue

        palabras = tokenizar(texto)

        paso = TAMANO_FRAGMENTO - SOLAPAMIENTO

        for inicio in range(0, len(palabras), paso):

            fragmento = palabras[
                inicio:inicio + TAMANO_FRAGMENTO
            ]

            if len(fragmento) < 20:
                continue

            contenido = " ".join(fragmento)

            cursor.execute("""
                INSERT INTO fragmentos
                (archivo, contenido)
                VALUES (?, ?)
            """, (
                str(archivo),
                contenido
            ))

            total += 1

    conexion.commit()

    print("Fragmentos almacenados:", total)


# ----------------------------------------
# 4. Construir índice estadístico
# ----------------------------------------

def construir_indice():

    cursor.execute("""
        SELECT id, archivo, contenido
        FROM fragmentos
    """)

    registros = cursor.fetchall()

    if not registros:
        raise RuntimeError(
            "No hay documentos para analizar."
        )

    textos = [fila[2] for fila in registros]

    vectorizador = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=100000
    )

    matriz = vectorizador.fit_transform(textos)

    print("Vocabulario:", len(
        vectorizador.vocabulary_
    ))

    return registros, vectorizador, matriz


# ----------------------------------------
# 5. Recuperar fragmentos relevantes
# ----------------------------------------

def buscar_contexto(
    pregunta,
    registros,
    vectorizador,
    matriz
):

    vector_pregunta = vectorizador.transform(
        [pregunta]
    )

    similitudes = cosine_similarity(
        vector_pregunta,
        matriz
    )[0]

    indices = similitudes.argsort()[::-1]

    seleccionados = []

    for indice in indices:

        puntuacion = float(similitudes[indice])

        if puntuacion <= 0:
            break

        seleccionados.append((
            puntuacion,
            registros[indice][2]
        ))

        if len(seleccionados) >= FRAGMENTOS_RELEVANTES:
            break

    return seleccionados


# ----------------------------------------
# 6. Crear modelo de n-gramas
# ----------------------------------------

def construir_modelo(fragmentos):

    modelo = {
        n: defaultdict(Counter)
        for n in range(1, VENTANA + 1)
    }

    frecuencias = Counter()

    for puntuacion, contenido in fragmentos:

        palabras = tokenizar(contenido)

        # Más importancia a documentos relevantes
        peso = max(1, round(puntuacion * 20))

        frecuencias.update({
            palabra: peso * cantidad
            for palabra, cantidad
            in Counter(palabras).items()
        })

        for i in range(1, len(palabras)):

            siguiente = palabras[i]

            for n in range(
                1,
                min(VENTANA, i) + 1
            ):

                contexto = tuple(
                    palabras[i-n:i]
                )

                modelo[n][contexto][siguiente] += peso

    return modelo, frecuencias


# ----------------------------------------
# 7. Detectar repeticiones
# ----------------------------------------

def repeticion(palabras, candidata):

    secuencia = palabras + [candidata]

    for longitud in range(1, 6):

        if len(secuencia) < longitud * 2:
            continue

        ultimo = secuencia[-longitud:]

        anterior = secuencia[
            -2*longitud:-longitud
        ]

        if ultimo == anterior:
            return True

    return False


# ----------------------------------------
# 8. Predecir siguiente palabra
# ----------------------------------------

def predecir(palabras, modelo, frecuencias):

    contexto = palabras[-VENTANA:]

    for n in range(
        min(VENTANA, len(contexto)),
        0,
        -1
    ):

        clave = tuple(contexto[-n:])

        candidatos = modelo[n].get(clave)

        if not candidatos:
            continue

        opciones = []
        pesos = []

        for palabra, frecuencia in candidatos.items():

            if repeticion(palabras, palabra):
                continue

            recientes = palabras[-25:]

            veces = recientes.count(palabra)

            penalizacion = 1 / (1 + veces * 3)

            opciones.append(palabra)

            pesos.append(
                frecuencia * penalizacion
            )

        if opciones:

            return random.choices(
                opciones,
                weights=pesos,
                k=1
            )[0]

    # Si no existe contexto, usar frecuencias
    opciones = []
    pesos = []

    for palabra, frecuencia in frecuencias.items():

        if repeticion(palabras, palabra):
            continue

        veces = palabras[-25:].count(palabra)

        opciones.append(palabra)

        pesos.append(
            frecuencia / (1 + veces * 3)
        )

    if not opciones:
        return None

    return random.choices(
        opciones,
        weights=pesos,
        k=1
    )[0]


# ----------------------------------------
# 9. Generar respuesta de 100 palabras
# ----------------------------------------

def generar_respuesta(pregunta, fragmentos):

    modelo, frecuencias = construir_modelo(
        fragmentos
    )

    # Arrancar con una secuencia real del corpus,
    # relacionada con la pregunta.
    palabras_pregunta = set(tokenizar(pregunta))

    semillas = []

    for puntuacion, contenido in fragmentos:

        palabras = tokenizar(contenido)

        for i in range(
            0,
            max(0, len(palabras) - 5)
        ):

            secuencia = palabras[i:i+5]

            coincidencias = len(
                set(secuencia) & palabras_pregunta
            )

            if coincidencias:
                semillas.append((
                    coincidencias * puntuacion,
                    secuencia
                ))

    if semillas:

        semillas.sort(
            key=lambda x: x[0],
            reverse=True
        )

        inicio = random.choice(
            semillas[:min(5, len(semillas))]
        )[1]

        respuesta = inicio.copy()

    else:

        respuesta = tokenizar(
            fragmentos[0][1]
        )[:5]

    # Generar hasta 100 palabras
    while len(respuesta) < LONGITUD_RESPUESTA:

        siguiente = predecir(
            respuesta,
            modelo,
            frecuencias
        )

        if siguiente is None:
            break

        respuesta.append(siguiente)

    texto = " ".join(
        respuesta[:LONGITUD_RESPUESTA]
    )

    return texto[0].upper() + texto[1:] + "."


# ----------------------------------------
# 10. Programa principal
# ----------------------------------------

def main():

    CARPETA.mkdir(exist_ok=True)

    print("================================")
    print(" GENERADOR ESTADÍSTICO DOCUMENTAL")
    print("================================")

    cargar_documentos()

    registros, vectorizador, matriz = (
        construir_indice()
    )

    print("\nSistema preparado.")
    print("Escribe una pregunta.")
    print("Escribe 'salir' para terminar.")

    while True:

        pregunta = input(
            "\nPregunta: "
        ).strip()

        if pregunta.lower() == "salir":
            break

        if not pregunta:
            continue

        fragmentos = buscar_contexto(
            pregunta,
            registros,
            vectorizador,
            matriz
        )

        if not fragmentos:

            print(
                "\nNo encuentro información "
                "relacionada con la pregunta."
            )

            continue

        print("\nFragmentos encontrados:")

        for puntuacion, contenido in fragmentos[:3]:

            print(
                f"  Similitud: {puntuacion:.3f}"
            )

            print(
                " ",
                contenido[:150],
                "..."
            )

        respuesta = generar_respuesta(
            pregunta,
            fragmentos
        )

        print("\nRESPUESTA GENERADA")
        print("--------------------------------")
        print(respuesta)
        print("--------------------------------")

        print(
            "Palabras:",
            len(tokenizar(respuesta))
        )

    conexion.close()


if __name__ == "__main__":
    main()
