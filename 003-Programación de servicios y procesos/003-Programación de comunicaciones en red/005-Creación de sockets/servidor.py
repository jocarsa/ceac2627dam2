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

        conexion.settimeout(3)

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

        print("Receptor desconectado")


def distribuir(imagen):

    with lock:
        colas = list(receptores.values())

    for cola in colas:

        # Descartar el fotograma anterior
        if cola.full():
            try:
                cola.get_nowait()
            except queue.Empty:
                pass

        try:
            cola.put_nowait(imagen)
        except queue.Full:
            pass


def atender(conexion, direccion):

    global emisor_activo

    print("Conexión:", direccion)

    es_emisor = False
    es_receptor = False

    try:

        conexion.settimeout(5)
        tipo = recibir_exacto(conexion, 1)

        if tipo == b"E":

            with lock:

                if emisor_activo:
                    return

                emisor_activo = True
                es_emisor = True

            print("Emisor conectado")

            conexion.settimeout(10)

            while True:

                cabecera = recibir_exacto(conexion, 4)
                longitud = struct.unpack("!I", cabecera)[0]

                if longitud == 0 or longitud > MAX_FRAME:
                    break

                imagen = recibir_exacto(conexion, longitud)

                distribuir(imagen)

        elif tipo == b"R":

            cola = queue.Queue(maxsize=1)

            with lock:
                receptores[conexion] = cola

            es_receptor = True

            print("Receptores:", len(receptores))

            enviar_receptor(conexion, cola)

    except (OSError, ConnectionError) as error:
        print("Conexión finalizada:", error)

    finally:

        if es_emisor:
            with lock:
                emisor_activo = False

        if not es_receptor:
            conexion.close()


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

servidor.bind((IP, PUERTO))
servidor.listen(20)

print(f"Servidor escuchando en {IP}:{PUERTO}")

while True:

    conexion, direccion = servidor.accept()

    threading.Thread(
        target=atender,
        args=(conexion, direccion),
        daemon=True
    ).start()