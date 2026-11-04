import socket
import struct
import threading
import queue
import tkinter as tk

import cv2
import numpy as np
from PIL import Image, ImageTk

IP = "10.4.193.182"
PUERTO = 5000

cola = queue.Queue(maxsize=2)
activo = True

ventana = tk.Tk()
ventana.title("Receptor de webcam")

etiqueta = tk.Label(ventana)
etiqueta.pack()

estado = tk.Label(ventana, text="Conectando...")
estado.pack()

conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def recibir_exacto(cantidad):
    datos = bytearray()

    while len(datos) < cantidad:
        bloque = conexion.recv(cantidad - len(datos))

        if not bloque:
            raise ConnectionError("Desconectado")

        datos.extend(bloque)

    return bytes(datos)


def recibir():
    try:
        conexion.connect((IP, PUERTO))
        conexion.sendall(b"R")

        while activo:
            cabecera = recibir_exacto(4)
            longitud = struct.unpack("!I", cabecera)[0]

            if longitud == 0 or longitud > 2 * 1024 * 1024:
                break

            datos = recibir_exacto(longitud)

            frame = cv2.imdecode(
                np.frombuffer(datos, dtype=np.uint8),
                cv2.IMREAD_COLOR
            )

            if frame is None:
                continue

            if cola.full():
                try:
                    cola.get_nowait()
                except queue.Empty:
                    pass

            cola.put_nowait(frame)

    except (OSError, ConnectionError) as error:
        print("Conexión finalizada:", error)


def actualizar():
    if not activo:
        return

    try:
        frame = cola.get_nowait()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        imagen = Image.fromarray(frame)
        foto = ImageTk.PhotoImage(imagen)

        etiqueta.configure(image=foto)
        etiqueta.image = foto

        estado.config(text="Recibiendo vídeo")

    except queue.Empty:
        pass

    ventana.after(30, actualizar)


def cerrar():
    global activo

    activo = False
    conexion.close()
    ventana.destroy()


ventana.protocol("WM_DELETE_WINDOW", cerrar)

threading.Thread(
    target=recibir,
    daemon=True
).start()

actualizar()
ventana.mainloop()