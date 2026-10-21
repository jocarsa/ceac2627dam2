import sqlite3
import requests
import json
import re
import time

# ----------------------------------------
# 1. Configuración
# ----------------------------------------

ARCHIVO = "lemario.txt"
BASE_DATOS = "lemario_vectores.db"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "granite4.1:8b"

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
    d.strip()
    for d in DIMENSIONES.replace("\n", " ").split(",")
    if d.strip()
]

NUM_DIMENSIONES = len(lista_dimensiones)

print("Dimensiones:", NUM_DIMENSIONES)

# ----------------------------------------
# 2. Base de datos SQLite
# ----------------------------------------

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

conexion.commit()

# ----------------------------------------
# 3. Generar vector con Ollama
# ----------------------------------------

def generar_vector(palabra):

    prompt = f"""
Dame un array de valores entre 0 y 1 de la palabra "{palabra}"
en base a estas dimensiones:

{DIMENSIONES}

REGLAS OBLIGATORIAS:
- Devuelve únicamente un array JSON.
- Sin explicaciones.
- Sin comentarios.
- Sin bloques markdown.
- Exactamente {NUM_DIMENSIONES} valores.
- Cada valor debe estar entre 0 y 1.
- Todos los valores deben tener decimales.
- No puedes utilizar 0.0 ni 1.0.
- Utiliza valores intermedios.
- Respeta exactamente el orden de las dimensiones.

Ejemplo de formato:
[0.23, 0.85, 0.12, 0.67]
"""

    respuesta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
                "num_predict": 2048
            }
        },
        timeout=600
    )

    respuesta.raise_for_status()

    texto = respuesta.json()["response"].strip()

    # Extraer el array
    coincidencia = re.search(
        r"\[[\s\S]*?\]",
        texto
    )

    if not coincidencia:
        raise ValueError("No se encontró un array JSON")

    vector = json.loads(coincidencia.group())

    # Validar número de dimensiones
    if len(vector) != NUM_DIMENSIONES:
        raise ValueError(
            f"Esperadas {NUM_DIMENSIONES} dimensiones, "
            f"recibidas {len(vector)}"
        )

    # Validar valores
    for valor in vector:

        if type(valor) not in (int, float):
            raise ValueError("Valor no numérico")

        if not 0 < valor < 1:
            raise ValueError(
                f"Valor fuera de rango: {valor}"
            )

    return vector


# ----------------------------------------
# 4. Leer lemario
# ----------------------------------------

with open(ARCHIVO, "r", encoding="utf-8") as archivo:
    palabras = [
        linea.strip()
        for linea in archivo
        if linea.strip()
    ]

print("Palabras encontradas:", len(palabras))

# ----------------------------------------
# 5. Procesar palabras
# ----------------------------------------

for indice, palabra in enumerate(palabras, 1):

    # Comprobar si ya existe
    cursor.execute(
        "SELECT id FROM palabras WHERE palabra = ?",
        (palabra,)
    )

    if cursor.fetchone():
        print(
            f"[{indice}/{len(palabras)}] "
            f"{palabra} - ya existe"
        )
        continue

    print(
        f"[{indice}/{len(palabras)}] "
        f"Procesando: {palabra}"
    )

    try:

        vector = generar_vector(palabra)

        cursor.execute("""
            INSERT INTO palabras (palabra, vector)
            VALUES (?, ?)
        """, (
            palabra,
            json.dumps(vector)
        ))

        conexion.commit()

        print(
            f"  OK - {len(vector)} dimensiones"
        )

    except Exception as error:

        print(
            f"  ERROR: {error}"
        )

        continue


# ----------------------------------------
# 6. Estadísticas finales
# ----------------------------------------

cursor.execute(
    "SELECT COUNT(*) FROM palabras"
)

total = cursor.fetchone()[0]

print("\n----------------------------")
print("PROCESO FINALIZADO")
print("----------------------------")
print("Palabras almacenadas:", total)
print("Dimensiones:", NUM_DIMENSIONES)
print("Base de datos:", BASE_DATOS)

conexion.close()