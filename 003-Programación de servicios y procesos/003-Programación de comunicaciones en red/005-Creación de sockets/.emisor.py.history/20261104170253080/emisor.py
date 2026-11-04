import socket
import struct
import threading
import tkinter as tk

import cv2
from PIL import Image, ImageTk

IP = "10.4.193.182"
PUERTO = 5000

activo = True

conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conexion.connect((IP, PUERTO))
conexion.sendall(b"E")

camara = cv2.VideoCapture(0)
camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ventana = tk.Tk()
ventana.title("Emisor de webcam")

etiqueta = tk.Label(ventana)
etiqueta.pack()

estado = tk.Label(ventana, text="Transmitiendo...")
estado.pack()


def transmitir():
    global activo

    while activo:
        correcto, frame = camara.read()

        if not correcto:
            break

        frame = cv2.resize(frame, (640, 480))

        correcto, comprimida = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 60]
        )

        if not correcto:
            continue

        datos = comprimida.tobytes()

        try:
            conexion.sendall(
                struct.pack("!I", len(datos)) + datos
            )
        except OSError:
            break

    activo = False


def actualizar():
    if not activo:
        return

    correcto, frame = camara.read()

    if correcto:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        imagen = Image.fromarray(frame)
        foto = ImageTk.PhotoImage(imagen)

        etiqueta.configure(image=foto)
        etiqueta.image = foto

    ventana.after(33, actualizar)


def cerrar():
    global activo

    activo = False
    camara.release()
    conexion.close()
    ventana.destroy()


ventana.protocol("WM_DELETE_WINDOW", cerrar)

threading.Thread(
    target=transmitir,
    daemon=True
).start()

actualizar()
ventana.mainloop()