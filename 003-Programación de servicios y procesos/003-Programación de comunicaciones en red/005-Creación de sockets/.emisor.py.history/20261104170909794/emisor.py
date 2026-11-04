import socket
import struct
import threading
import queue
import tkinter as tk

import cv2
from PIL import Image, ImageTk

IP = "10.4.193.182"
PUERTO = 5000

FPS = 15
CALIDAD = 60

cola = queue.Queue(maxsize=1)
activo = True

camara = cv2.VideoCapture(0)

camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ventana = tk.Tk()
ventana.title("Emisor webcam")

etiqueta = tk.Label(ventana)
etiqueta.pack()

estado = tk.Label(ventana, text="Conectando...")
estado.pack()


def transmitir():
    global activo

    try:
        conexion = socket.create_connection(
            (IP, PUERTO),
            timeout=5
        )

        conexion.settimeout(5)
        conexion.sendall(b"E")

        print("Conectado al servidor")

        while activo:

            try:
                frame = cola.get(timeout=0.5)
            except queue.Empty:
                continue

            correcto, comprimida = cv2.imencode(
                ".jpg",
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, CALIDAD]
            )

            if not correcto:
                continue

            datos = comprimida.tobytes()

            conexion.sendall(
                struct.pack("!I", len(datos)) + datos
            )

    except (OSError, ConnectionError) as error:
        print("Error de transmisión:", error)

    finally:
        activo = False
        try:
            conexion.close()
        except UnboundLocalError:
            pass


def actualizar():

    if not activo:
        estado.config(text="Transmisión detenida")
        return

    correcto, frame = camara.read()

    if correcto:

        frame = cv2.resize(frame, (640, 480))

        # Enviar el fotograma más reciente
        if cola.full():
            try:
                cola.get_nowait()
            except queue.Empty:
                pass

        try:
            cola.put_nowait(frame.copy())
        except queue.Full:
            pass

        # Mostrar webcam local
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        imagen = Image.fromarray(rgb)
        foto = ImageTk.PhotoImage(imagen)

        etiqueta.configure(image=foto)
        etiqueta.image = foto

        estado.config(text="Capturando webcam")

    ventana.after(int(1000 / FPS), actualizar)


def cerrar():
    global activo

    activo = False
    camara.release()
    ventana.destroy()


ventana.protocol("WM_DELETE_WINDOW", cerrar)

threading.Thread(
    target=transmitir,
    daemon=True
).start()

actualizar()
ventana.mainloop()