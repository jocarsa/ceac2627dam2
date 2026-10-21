
import sqlite3
import re
from collections import Counter

ARCHIVO = "cursojava.txt"
BASE_DATOS = "palabras.db"
VENTANA = 10

# -----------------------------------
# 1. Leer archivo
# -----------------------------------

with open(ARCHIVO, "r", encoding="utf-8") as archivo:
    texto = archivo.read().lower()

palabras = re.findall(r"\b\w+\b", texto, flags=re.UNICODE)

print("Total de palabras:", len(palabras))
print("Palabras diferentes:", len(set(palabras)))

# -----------------------------------
# 2. Conectar SQLite
# -----------------------------------

conexion = sqlite3.connect(BASE_DATOS)
cursor = conexion.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS palabras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    palabra TEXT UNIQUE,
    frecuencia INTEGER
);

CREATE TABLE IF NOT EXISTS contextos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    palabra_id INTEGER,
    posicion INTEGER,
    anteriores TEXT,
    posteriores TEXT,
    contexto_completo TEXT,
    FOREIGN KEY (palabra_id) REFERENCES palabras(id)
);

CREATE TABLE IF NOT EXISTS relaciones (
    palabra_id INTEGER,
    relacionada_id INTEGER,
    distancia INTEGER,
    direccion TEXT,
    frecuencia INTEGER,
    PRIMARY KEY (
        palabra_id,
        relacionada_id,
        distancia,
        direccion
    )
);

CREATE INDEX IF NOT EXISTS idx_contextos_palabra
ON contextos(palabra_id);

CREATE INDEX IF NOT EXISTS idx_relaciones_palabra
ON relaciones(palabra_id);
""")

# Reconstruir estadísticas en cada ejecución
cursor.execute("DELETE FROM relaciones")
cursor.execute("DELETE FROM contextos")
cursor.execute("DELETE FROM palabras")

conexion.commit()

# -----------------------------------
# 3. Contar palabras
# -----------------------------------

frecuencias = Counter(palabras)

cursor.executemany(
    "INSERT INTO palabras (palabra, frecuencia) VALUES (?, ?)",
    frecuencias.items()
)

conexion.commit()

cursor.execute("SELECT id, palabra FROM palabras")
ids = {palabra: identificador for identificador, palabra in cursor.fetchall()}

# -----------------------------------
# 4. Crear contextos y relaciones
# -----------------------------------

relaciones = Counter()
lote_contextos = []

for posicion, palabra in enumerate(palabras):

    inicio = max(0, posicion - VENTANA)
    fin = min(len(palabras), posicion + VENTANA + 1)

    anteriores = palabras[inicio:posicion]
    posteriores = palabras[posicion + 1:fin]

    contexto = palabras[inicio:fin]

    palabra_id = ids[palabra]

    lote_contextos.append((
        palabra_id,
        posicion,
        " ".join(anteriores),
        " ".join(posteriores),
        " ".join(contexto)
    ))

    # Palabras anteriores
    for distancia, relacionada in enumerate(
        reversed(anteriores), start=1
    ):
        clave = (
            palabra_id,
            ids[relacionada],
            distancia,
            "anterior"
        )
        relaciones[clave] += 1

    # Palabras posteriores
    for distancia, relacionada in enumerate(
        posteriores, start=1
    ):
        clave = (
            palabra_id,
            ids[relacionada],
            distancia,
            "posterior"
        )
        relaciones[clave] += 1

    if len(lote_contextos) >= 5000:
        cursor.executemany("""
            INSERT INTO contextos (
                palabra_id, posicion, anteriores,
                posteriores, contexto_completo
            ) VALUES (?, ?, ?, ?, ?)
        """, lote_contextos)

        conexion.commit()
        lote_contextos.clear()

    if posicion % 10000 == 0:
        print("Procesadas:", posicion)

# Guardar contextos restantes
if lote_contextos:
    cursor.executemany("""
        INSERT INTO contextos (
            palabra_id, posicion, anteriores,
            posteriores, contexto_completo
        ) VALUES (?, ?, ?, ?, ?)
    """, lote_contextos)

# Guardar relaciones agregadas
cursor.executemany("""
    INSERT INTO relaciones (
        palabra_id, relacionada_id,
        distancia, direccion, frecuencia
    ) VALUES (?, ?, ?, ?, ?)
""", [
    (*clave, cantidad)
    for clave, cantidad in relaciones.items()
])

conexion.commit()

# -----------------------------------
# 5. Mostrar las 100 más frecuentes
# -----------------------------------

print("\n100 PALABRAS MÁS FRECUENTES")
print("--------------------------------")

cursor.execute("""
SELECT palabra, frecuencia
FROM palabras
ORDER BY frecuencia DESC
LIMIT 100
""")

for palabra, cantidad in cursor.fetchall():
    print(palabra, ":", cantidad)

# -----------------------------------
# 6. Consultar relaciones
# -----------------------------------

def consultar_palabra(palabra):

    cursor.execute("""
        SELECT
            p2.palabra,
            SUM(r.frecuencia) AS total
        FROM relaciones r
        JOIN palabras p1 ON r.palabra_id = p1.id
        JOIN palabras p2 ON r.relacionada_id = p2.id
        WHERE p1.palabra = ?
        GROUP BY p2.id
        ORDER BY total DESC
        LIMIT 20
    """, (palabra,))

    print("\nPalabras relacionadas con:", palabra)

    for relacionada, frecuencia in cursor.fetchall():
        print(relacionada, ":", frecuencia)


while True:

    palabra = input("\nConsultar palabra (salir): ").lower().strip()

    if palabra == "salir":
        break

    consultar_palabra(palabra)

conexion.close()
