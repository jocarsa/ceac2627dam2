import sqlite3
import re
import random
import time

from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ----------------------------------------
# 0. CONFIGURACIÓN
# ----------------------------------------

CARPETA = Path("/var/www/html/clases/")
BASE_DATOS = "conocimiento.db"

VENTANA = 10
LONGITUD_RESPUESTA = 100
TAMANO_FRAGMENTO = 200
SOLAPAMIENTO = 40
FRAGMENTOS_RELEVANTES = 8


# ----------------------------------------
# UTILIDADES PARA MEDIR TIEMPOS
# ----------------------------------------

def fecha_actual():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def mostrar_tiempo(nombre, segundos):

    print(
        f"{nombre}: {segundos:.4f} segundos"
    )


# ----------------------------------------
# 1. BASE DE DATOS
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
# 2. TOKENIZACIÓN
# ----------------------------------------

def tokenizar(texto):

    return re.findall(
        r"\b\w+\b",
        texto.lower(),
        flags=re.UNICODE
    )


# ----------------------------------------
# 3. LEER DOCUMENTOS DE CARPETA
# ----------------------------------------

def cargar_documentos():

    inicio = time.perf_counter()

    print("\n================================")
    print(" CARGANDO DOCUMENTOS")
    print("================================")

    print("Inicio:", fecha_actual())

    cursor.execute("DELETE FROM fragmentos")

    archivos = list(CARPETA.rglob("*.txt"))

    print("Archivos encontrados:", len(archivos))

    total = 0
    palabras_totales = 0

    paso = TAMANO_FRAGMENTO - SOLAPAMIENTO

    for numero, archivo in enumerate(archivos, 1):

        try:

            texto = archivo.read_text(
                encoding="utf-8"
            )

        except UnicodeError:

            print("No se pudo leer:", archivo)
            continue

        palabras = tokenizar(texto)

        palabras_totales += len(palabras)

        for posicion in range(
            0,
            len(palabras),
            paso
        ):

            fragmento = palabras[
                posicion:posicion + TAMANO_FRAGMENTO
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

        if numero % 100 == 0:

            print(
                f"Procesados {numero}/{len(archivos)} archivos"
            )

    conexion.commit()

    fin = time.perf_counter()

    duracion = fin - inicio

    print("\nDocumentos procesados:", len(archivos))
    print("Palabras procesadas:", palabras_totales)
    print("Fragmentos almacenados:", total)

    print("Final:", fecha_actual())

    mostrar_tiempo(
        "Tiempo de carga",
        duracion
    )

    return duracion


# ----------------------------------------
# 4. CONSTRUIR ÍNDICE ESTADÍSTICO
# ----------------------------------------

def construir_indice():

    inicio = time.perf_counter()

    print("\n================================")
    print(" CONSTRUYENDO ÍNDICE TF-IDF")
    print("================================")

    print("Inicio:", fecha_actual())

    cursor.execute("""
        SELECT id, archivo, contenido
        FROM fragmentos
    """)

    registros = cursor.fetchall()

    if not registros:

        raise RuntimeError(
            "No hay documentos para analizar."
        )

    textos = [
        fila[2]
        for fila in registros
    ]

    vectorizador = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=100000
    )

    matriz = vectorizador.fit_transform(textos)

    fin = time.perf_counter()

    duracion = fin - inicio

    print("Fragmentos indexados:", len(registros))

    print(
        "Vocabulario:",
        len(vectorizador.vocabulary_)
    )

    print("Dimensiones de la matriz:", matriz.shape)

    print("Final:", fecha_actual())

    mostrar_tiempo(
        "Tiempo de indexación",
        duracion
    )

    return registros, vectorizador, matriz, duracion


# ----------------------------------------
# 5. RECUPERAR FRAGMENTOS RELEVANTES
# ----------------------------------------

def buscar_contexto(
    pregunta,
    registros,
    vectorizador,
    matriz
):

    inicio = time.perf_counter()

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

        puntuacion = float(
            similitudes[indice]
        )

        if puntuacion <= 0:
            break

        seleccionados.append((
            puntuacion,
            registros[indice][2]
        ))

        if len(seleccionados) >= FRAGMENTOS_RELEVANTES:
            break

    fin = time.perf_counter()

    duracion = fin - inicio

    return seleccionados, duracion


# ----------------------------------------
# 6. CREAR MODELO DE N-GRAMAS
# ----------------------------------------

def construir_modelo(fragmentos):

    inicio = time.perf_counter()

    modelo = {
        n: defaultdict(Counter)
        for n in range(1, VENTANA + 1)
    }

    frecuencias = Counter()

    total_contextos = 0

    for puntuacion, contenido in fragmentos:

        palabras = tokenizar(contenido)

        # Más importancia a documentos relevantes
        peso = max(
            1,
            round(puntuacion * 20)
        )

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

                total_contextos += 1

    fin = time.perf_counter()

    duracion = fin - inicio

    return (
        modelo,
        frecuencias,
        duracion,
        total_contextos
    )


# ----------------------------------------
# 7. DETECTAR REPETICIONES
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
# 8. PREDECIR SIGUIENTE PALABRA
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
# 9. GENERAR RESPUESTA
# ----------------------------------------

def generar_respuesta(pregunta, fragmentos):

    inicio_total = time.perf_counter()

    # Entrenamiento del modelo de n-gramas

    (
        modelo,
        frecuencias,
        tiempo_entrenamiento,
        total_contextos
    ) = construir_modelo(fragmentos)

    inicio_generacion = time.perf_counter()

    # Buscar semillas relacionadas con la pregunta

    palabras_pregunta = set(
        tokenizar(pregunta)
    )

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

    # Generar palabras

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

    if texto:
        texto = texto[0].upper() + texto[1:] + "."

    fin = time.perf_counter()

    tiempo_generacion = fin - inicio_generacion

    tiempo_total = fin - inicio_total

    estadisticas = {
        "entrenamiento": tiempo_entrenamiento,
        "generacion": tiempo_generacion,
        "total": tiempo_total,
        "contextos": total_contextos,
        "palabras": len(respuesta)
    }

    return texto, estadisticas


# ----------------------------------------
# 10. MOSTRAR ESTADÍSTICAS
# ----------------------------------------

def mostrar_estadisticas_iniciales(
    fecha_inicio,
    fecha_fin,
    tiempo_carga,
    tiempo_indice,
    tiempo_total
):

    print("\n")
    print("========================================")
    print(" INFORME DE ENTRENAMIENTO INICIAL")
    print("========================================")

    print("Inicio:", fecha_inicio)
    print("Final: ", fecha_fin)

    print("----------------------------------------")

    mostrar_tiempo(
        "Carga de documentos",
        tiempo_carga
    )

    mostrar_tiempo(
        "Construcción TF-IDF",
        tiempo_indice
    )

    print("----------------------------------------")

    mostrar_tiempo(
        "TIEMPO TOTAL",
        tiempo_total
    )

    print("========================================")


def mostrar_estadisticas_respuesta(
    estadisticas,
    tiempo_busqueda,
    fecha_inicio,
    fecha_fin
):

    print("\n========================================")
    print(" ESTADÍSTICAS DE GENERACIÓN")
    print("========================================")

    print("Inicio:", fecha_inicio)
    print("Final: ", fecha_fin)

    print("----------------------------------------")

    mostrar_tiempo(
        "Búsqueda de contexto",
        tiempo_busqueda
    )

    mostrar_tiempo(
        "Entrenamiento n-gramas",
        estadisticas["entrenamiento"]
    )

    mostrar_tiempo(
        "Generación de respuesta",
        estadisticas["generacion"]
    )

    print("----------------------------------------")

    mostrar_tiempo(
        "TIEMPO TOTAL",
        tiempo_busqueda + estadisticas["total"]
    )

    print("----------------------------------------")

    print(
        "Contextos procesados:",
        estadisticas["contextos"]
    )

    print(
        "Palabras generadas:",
        estadisticas["palabras"]
    )

    print("========================================")


# ----------------------------------------
# 11. PROGRAMA PRINCIPAL
# ----------------------------------------

def main():

    CARPETA.mkdir(
        parents=True,
        exist_ok=True
    )

    print("========================================")
    print(" GENERADOR ESTADÍSTICO DOCUMENTAL")
    print("========================================")

    # ------------------------------------
    # INICIO DEL ENTRENAMIENTO INICIAL
    # ------------------------------------

    fecha_inicio = fecha_actual()

    inicio_total = time.perf_counter()

    # Fase 1: cargar documentos

    tiempo_carga = cargar_documentos()

    # Fase 2: construir índice

    (
        registros,
        vectorizador,
        matriz,
        tiempo_indice
    ) = construir_indice()

    # ------------------------------------
    # FIN DEL ENTRENAMIENTO INICIAL
    # ------------------------------------

    fin_total = time.perf_counter()

    fecha_fin = fecha_actual()

    tiempo_total = fin_total - inicio_total

    mostrar_estadisticas_iniciales(
        fecha_inicio,
        fecha_fin,
        tiempo_carga,
        tiempo_indice,
        tiempo_total
    )

    print("\nSistema preparado.")

    print("Escribe una pregunta.")
    print("Escribe 'salir' para terminar.")

    # ------------------------------------
    # BUCLE DE PREGUNTAS
    # ------------------------------------

    while True:

        pregunta = input(
            "\nPregunta: "
        ).strip()

        if pregunta.lower() == "salir":
            break

        if not pregunta:
            continue

        fecha_inicio_pregunta = fecha_actual()

        # Buscar fragmentos relevantes

        (
            fragmentos,
            tiempo_busqueda
        ) = buscar_contexto(
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

        # Generar respuesta

        respuesta, estadisticas = generar_respuesta(
            pregunta,
            fragmentos
        )

        fecha_fin_pregunta = fecha_actual()

        print("\nRESPUESTA GENERADA")
        print("----------------------------------------")
        print(respuesta)
        print("----------------------------------------")

        mostrar_estadisticas_respuesta(
            estadisticas,
            tiempo_busqueda,
            fecha_inicio_pregunta,
            fecha_fin_pregunta
        )

    conexion.close()

    print("\nPrograma finalizado.")


# ----------------------------------------
# 12. EJECUCIÓN
# ----------------------------------------

if __name__ == "__main__":
    main()