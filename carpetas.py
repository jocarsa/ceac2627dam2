#!/usr/bin/env python3

import os
import re

ARCHIVO = "README.md"
DESTINO = "."

INTRO = "000-Introducción.md"


def limpiar_nombre(texto):
    texto = texto.strip()

    if texto.startswith("-"):
        texto = texto[1:].strip()

    texto = texto.rstrip(":").strip()

    texto = re.sub(r'[<>:"/\\|?*]', "", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto


def obtener_nivel(linea):
    """
    Soporta tanto espacios como tabulaciones.
    Cada 4 espacios = 1 nivel.
    Cada tab = 1 nivel.
    """

    prefijo = linea[:len(linea) - len(linea.lstrip(" \t"))]

    nivel = 0.0

    for c in prefijo:
        if c == "\t":
            nivel += 1
        elif c == " ":
            nivel += 0.25

    return int(nivel)


def crear_intro(ruta):
    intro = os.path.join(ruta, INTRO)

    if not os.path.exists(intro):

        titulo = os.path.basename(ruta)
        titulo = re.sub(r"^\d{3}-", "", titulo)

        with open(intro, "w", encoding="utf-8") as f:
            f.write(f"# {titulo}\n\n")


def procesar():

    pila = []

    # numeración empieza en 001
    contadores = {}

    with open(ARCHIVO, "r", encoding="utf-8") as f:

        for num_linea, linea in enumerate(f, start=1):

            if not linea.strip():
                continue

            linea_expandida = linea.expandtabs(4)

            if not linea_expandida.lstrip().startswith("- "):
                continue

            nivel = obtener_nivel(linea_expandida)
            nombre = limpiar_nombre(linea_expandida)

            if not nombre:
                continue

            while len(pila) > nivel:
                pila.pop()

            while len(pila) < nivel:
                print(
                    f"AVISO línea {num_linea}: "
                    f"salto de nivel inesperado. Ajustando."
                )
                nivel -= 1

            if nivel not in contadores:
                contadores[nivel] = 1

            for k in list(contadores.keys()):
                if k > nivel:
                    del contadores[k]

            numero = contadores[nivel]
            contadores[nivel] += 1

            carpeta = f"{numero:03d}-{nombre}"

            if nivel == 0:
                ruta = os.path.join(DESTINO, carpeta)
            else:
                ruta = os.path.join(pila[nivel - 1], carpeta)

            if not os.path.exists(ruta):
                os.makedirs(ruta)
                print("CREADA", ruta)
            else:
                print("EXISTE", ruta)

            crear_intro(ruta)

            if len(pila) == nivel:
                pila.append(ruta)
            else:
                pila[nivel] = ruta


if __name__ == "__main__":
    procesar()
