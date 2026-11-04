import socket
import threading
import queue
import struct

IP = "0.0.0.0"
PUERTO = 5000
MAX_FRAME = 2 * 1024 * 1024

receptores = {}
lock = threading.Lock()
emisor_activo = False


def recibir_exacto(conexion, cantidad):
    datos = bytearray()

    while len(datos) < cantidad:
        bloque = conexion.recv(cantidad - len(datos))

        if not bloque:
            raise ConnectionError("Conexión cerrada")

        datos.extend(bloque)

    return bytes(datos)


def enviar_receptor(conexion, cola):
    try:
        while True:
            imagen = cola.get()

            conexion.sendall(
                struct.pack("!I", len(imagen)) + imagen
            )

    except (OSError, ConnectionError):
        pass

    finally:
        with lock:
            receptores.pop(conexion, None)

        conexion.close()


def atender(conexion, direccion):
    global emisor_activo

    print("Conectado:", direccion)

    try:
        tipo = recibir_exacto(conexion, 1)

        if tipo == b"E":

            with lock:
                if emisor_activo:
                    conexion.close()
                    return

                emisor_activo = True

            print("Emisor conectado")

            try:
                while True:
                    cabecera = recibir_exacto(conexion, 4)
                    longitud = struct.unpack("!I", cabecera)[0]

                    if longitud == 0 or longitud > MAX_FRAME:
                        break

                    imagen = recibir_exacto(conexion, longitud)

                    with lock:
                        colas = list(receptores.values())

                    for cola in colas:
                        try:
                            cola.put_nowait(imagen)
                        except queue.Full:
                            try:
                                cola.get_nowait()
                                cola.put_nowait(imagen)
                            except queue.Empty:
                                pass

            finally:
                with lock:
                    emisor_activo = False

                print("Emisor desconectado")

        elif tipo == b"R":

            cola = queue.Queue(maxsize=2)

            with lock:
                receptores[conexion] = cola

            print("Receptores:", len(receptores))

            enviar_receptor(conexion, cola)

    except (OSError, ConnectionError):
        pass

    finally:
        conexion.close()


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((IP, PUERTO))
servidor.listen()

print(f"Servidor escuchando en {IP}:{PUERTO}")

while True:
    conexion, direccion = servidor.accept()

    threading.Thread(
        target=atender,
        args=(conexion, direccion),
        daemon=True
    ).start()