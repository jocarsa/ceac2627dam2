import sqlite3
import requests
import json
import time
import math
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

ARCHIVO = "lemario.txt"
BASE_DATOS = "lemario_vectores.db"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "granite4.1:8b"

MAX_REINTENTOS = 3
ESPERA_REINTENTO = 3
TIMEOUT = 600

DIMENSIONES = """
Existencia, Concreción, Materialidad, Ser vivo, Animal, Vegetal, Humano, Artificial,
Natural, Objeto, Sustancia, Energía, Fenómeno, Organismo, Entorno, Universo,
Espacialidad, Posición, Distancia, Dirección, Movimiento, Velocidad, Tamaño, Volumen,
Superficie, Forma, Estructura, Interioridad, Proximidad, Verticalidad, Horizontalidad, Contención,
Temporalidad, Pasado, Presente, Futuro, Duración, Frecuencia, Secuencia, Inicio,
Finalización, Cambio, Crecimiento, Disminución, Permanencia, Repetición, Antigüedad, Novedad,
Acción, Agente, Intencionalidad, Causalidad, Efecto, Creación, Destrucción, Construcción,
Transformación, Transferencia, Interacción, Control, Dependencia, Capacidad, Dificultad, Resultado,
Conocimiento, Aprendizaje, Memoria, Razonamiento, Inteligencia, Comprensión, Percepción, Atención,
Imaginación, Creatividad, Comunicación, Lenguaje, Simbolismo, Veracidad, Incertidumbre, Complejidad,
Emoción, Alegría, Tristeza, Miedo, Ira, Amor, Deseo, Placer,
Dolor, Motivación, Confianza, Ansiedad, Curiosidad, Empatía, Identidad, Conciencia,
Sociedad, Familia, Amistad, Cooperación, Competencia, Autoridad, Poder, Economía,
Comercio, Trabajo, Educación, Cultura, Política, Derecho, Moralidad, Religión,
Cantidad, Intensidad, Calidad, Utilidad, Belleza, Seguridad, Riesgo, Salud,
Enfermedad, Tecnología, Computación, Matemáticas, Ciencia, Arte, Abundancia, Escasez
"""

lista_dimensiones = [
    dimension.strip()
    for dimension in DIMENSIONES.replace("\n", " ").split(",")
    if dimension.strip()
]

NUM_DIMENSIONES = len(lista_dimensiones)

assert NUM_DIMENSIONES == 128, (
    f"Se esperaban 128 dimensiones y hay {NUM_DIMENSIONES}"
)

print("Dimensiones:", NUM_DIMENSIONES)


# ==========================================
# 2. CONECTAR A SQLITE
# ==========================================

conexion = sqlite3.connect(BASE_DATOS)

cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS palabras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    palabra TEXT UNIQUE NOT NULL,
    vector TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS errores (
    palabra TEXT PRIMARY KEY,
    error TEXT,
    intentos INTEGER DEFAULT 0,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS dimensiones (
    posicion INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
)
""")

for posicion, dimension in enumerate(lista_dimensiones):

    cursor.execute("""
        INSERT OR REPLACE INTO dimensiones
        (posicion, nombre)
        VALUES (?, ?)
    """, (posicion, dimension))

conexion.commit()


# ==========================================
# 3. ESQUEMA JSON OBLIGATORIO
# ==========================================

ESQUEMA_JSON = {
    "type": "object",
    "properties": {
        "vector": {
            "type": "array",
            "items": {
                "type": "number",
                "minimum": 0.001,
                "maximum": 0.999
            },
            "minItems": NUM_DIMENSIONES,
            "maxItems": NUM_DIMENSIONES
        }
    },
    "required": ["vector"],
    "additionalProperties": False
}


# ==========================================
# 4. CREAR PROMPT
# ==========================================

def crear_prompt(palabra):

    return f"""
Eres un sistema de análisis semántico.

Analiza la palabra:

{json.dumps(palabra, ensure_ascii=False)}

Debes generar un vector semántico de
exactamente {NUM_DIMENSIONES} dimensiones.

Cada dimensión representa una propiedad
semántica de la palabra.

DIMENSIONES EN ORDEN:

{DIMENSIONES}

INSTRUCCIONES:

1. Asigna un valor decimal a cada dimensión.
2. Cada valor debe estar entre 0.001 y 0.999.
3. No utilices nunca 0.0 ni 1.0.
4. Respeta estrictamente el orden.
5. No omitas ninguna dimensión.
6. Los valores deben representar la relación
   semántica entre la palabra y cada dimensión.
7. Utiliza valores altos para relaciones fuertes.
8. Utiliza valores bajos para relaciones débiles.
9. No escribas explicaciones.
10. Devuelve únicamente el objeto JSON solicitado.

La clave del objeto debe llamarse "vector".
"""


# ==========================================
# 5. GENERAR VECTOR CON OLLAMA
# ==========================================

def generar_vector(palabra):

    prompt = crear_prompt(palabra)

    respuesta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "prompt": prompt,
            "stream": False,
            "format": ESQUEMA_JSON,
            "keep_alive": "30m",
            "options": {
                "temperature": 0,
                "num_ctx": 4096,
                "num_predict": 4096
            }
        },
        timeout=TIMEOUT
    )

    respuesta.raise_for_status()

    datos = respuesta.json()

    texto = datos.get("response", "").strip()

    if not texto:
        raise ValueError(
            "Ollama devolvió una respuesta vacía. "
            f"Motivo: {datos.get('done_reason', 'desconocido')}"
        )

    try:
        resultado = json.loads(texto)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"JSON inválido: {error}. "
            f"Respuesta: {texto[:300]}"
        )

    if not isinstance(resultado, dict):
        raise ValueError(
            "La respuesta no es un objeto JSON"
        )

    vector = resultado.get("vector")

    if not isinstance(vector, list):
        raise ValueError(
            "No se encontró el array 'vector'"
        )

    if len(vector) != NUM_DIMENSIONES:
        raise ValueError(
            f"Dimensiones incorrectas: "
            f"{len(vector)}/{NUM_DIMENSIONES}"
        )

    for indice, valor in enumerate(vector):

        if type(valor) not in (int, float):
            raise ValueError(
                f"Valor no numérico en dimensión {indice}"
            )

        if not math.isfinite(valor) or not 0 < valor < 1:
            raise ValueError(
                f"Valor inválido en dimensión "
                f"{indice}: {valor}"
            )

    return [float(valor) for valor in vector]


# ==========================================
# 6. GENERAR CON REINTENTOS
# ==========================================

def generar_con_reintentos(palabra):

    ultimo_error = None

    for intento in range(1, MAX_REINTENTOS + 1):

        try:

            vector = generar_vector(palabra)

            return vector

        except (requests.RequestException, ValueError, KeyError) as error:

            ultimo_error = str(error)

            print(
                f"    Intento {intento}/{MAX_REINTENTOS}: "
                f"{ultimo_error}"
            )

            if intento < MAX_REINTENTOS:
                time.sleep(ESPERA_REINTENTO)

    raise RuntimeError(ultimo_error)


# ==========================================
# 7. LEER LEMARIO
# ==========================================

with open(ARCHIVO, "r", encoding="utf-8-sig") as archivo:

    palabras = [
        linea.strip()
        for linea in archivo
        if linea.strip()
    ]

# Eliminar duplicados respetando el orden

palabras = list(dict.fromkeys(palabras))

TOTAL = len(palabras)

print("\nPalabras encontradas:", TOTAL)


# ==========================================
# 8. RECUPERAR PROGRESO ANTERIOR
# ==========================================

cursor.execute("SELECT palabra FROM palabras")

procesadas = {
    fila[0]
    for fila in cursor.fetchall()
}

pendientes = [
    palabra
    for palabra in palabras
    if palabra not in procesadas
]

print("Ya procesadas:", len(procesadas))
print("Pendientes:", len(pendientes))

print("-----------------------------------")


# ==========================================
# 9. FORMATEAR TIEMPO
# ==========================================

def formatear_tiempo(segundos):

    segundos = int(segundos)

    dias, resto = divmod(segundos, 86400)
    horas, resto = divmod(resto, 3600)
    minutos, segundos = divmod(resto, 60)

    return (
        f"{dias}d "
        f"{horas}h "
        f"{minutos}m "
        f"{segundos}s"
    )


# ==========================================
# 10. PROCESAMIENTO PRINCIPAL
# ==========================================

inicio_global = time.time()

correctas = 0
fallidas = 0

tiempos = []

try:

    for indice, palabra in enumerate(pendientes, 1):

        inicio_palabra = time.time()

        print(
            f"\n[{indice}/{len(pendientes)}] "
            f"Procesando: {palabra}"
        )

        try:

            vector = generar_con_reintentos(palabra)

            # Guardar vector

            cursor.execute("""
                INSERT OR IGNORE INTO palabras
                (palabra, vector)
                VALUES (?, ?)
            """, (
                palabra,
                json.dumps(
                    vector,
                    ensure_ascii=False
                )
            ))

            # Eliminar error anterior si existía

            cursor.execute("""
                DELETE FROM errores
                WHERE palabra = ?
            """, (palabra,))

            conexion.commit()

            correctas += 1

            print(
                f"    OK - {len(vector)} dimensiones"
            )

        except Exception as error:

            fallidas += 1

            cursor.execute("""
                INSERT INTO errores
                (palabra, error, intentos, fecha)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(palabra)
                DO UPDATE SET
                    error = excluded.error,
                    intentos = errores.intentos + excluded.intentos,
                    fecha = CURRENT_TIMESTAMP
            """, (
                palabra,
                str(error),
                MAX_REINTENTOS
            ))

            conexion.commit()

            print(
                f"    ERROR DEFINITIVO: {error}"
            )

        # ----------------------------------
        # Estadísticas de velocidad
        # ----------------------------------

        duracion = time.time() - inicio_palabra

        tiempos.append(duracion)

        # Media móvil de últimas 50 palabras

        ultimos = tiempos[-50:]

        media = sum(ultimos) / len(ultimos)

        restantes = len(pendientes) - indice

        estimacion = media * restantes

        porcentaje = indice / len(pendientes) * 100

        print(
            f"    Tiempo palabra: {duracion:.2f}s"
        )

        print(
            f"    Progreso: {porcentaje:.2f}%"
        )

        print(
            f"    Correctas: {correctas} | "
            f"Errores: {fallidas}"
        )

        print(
            f"    Tiempo restante estimado: "
            f"{formatear_tiempo(estimacion)}"
        )

        fecha_estimada = (
            datetime.now()
            + timedelta(seconds=estimacion)
        )

        print(
            f"    Finalización estimada: "
            f"{fecha_estimada:%Y-%m-%d %H:%M:%S}"
        )

except KeyboardInterrupt:

    print("\nProceso interrumpido por el usuario.")
    print("El progreso está guardado en SQLite.")

finally:

    # ======================================
    # 11. ESTADÍSTICAS FINALES
    # ======================================

    cursor.execute("""
        SELECT COUNT(*) FROM palabras
    """)

    total_guardadas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM errores
    """)

    total_errores = cursor.fetchone()[0]

    tiempo_total = time.time() - inicio_global

    print("\n===================================")
    print("RESUMEN")
    print("===================================")

    print("Palabras del lemario:", TOTAL)
    print("Vectores almacenados:", total_guardadas)
    print("Errores pendientes:", total_errores)
    print("Dimensiones:", NUM_DIMENSIONES)

    print(
        "Tiempo de ejecución:",
        formatear_tiempo(tiempo_total)
    )

    print("Base de datos:", BASE_DATOS)

    conexion.close()