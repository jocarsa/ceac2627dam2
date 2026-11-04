import socket
import threading
import time
from collections import deque

IP = "10.4.193.182"
PUERTO = 5000

# CONFIGURACIÓN
MAX_MENSAJES_MINUTO = 10
MAX_CARACTERES = 200
SEGUNDOS_BLOQUEO = 60

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((IP, PUERTO))
servidor.listen()

clientes = []
lock = threading.Lock()

print(f"Servidor escuchando en {IP}:{PUERTO}")


def atender_cliente(conexion, direccion):
    print("Cliente conectado:", direccion)

    historial = deque()
    bloqueado_hasta = 0

    with lock:
        clientes.append(conexion)

    try:
        buffer = b""

        while True:
            datos = conexion.recv(4096)

            if not datos:
                break

            buffer += datos

            # Cada mensaje termina con salto de línea
            while b"\n" in buffer:
                linea, buffer = buffer.split(b"\n", 1)

                ahora = time.monotonic()

                # COMPROBAR BLOQUEO
                if ahora < bloqueado_hasta:
                    restantes = int(bloqueado_hasta - ahora) + 1
                    conexion.sendall(
                        f"Bloqueado. Espera {restantes} segundos.\n".encode()
                    )
                    continue

                try:
                    mensaje = linea.decode("utf-8")
                except UnicodeDecodeError:
                    conexion.sendall(b"Mensaje UTF-8 invalido.\n")
                    continue

                # COMPROBAR CARACTERES
                if len(mensaje) > MAX_CARACTERES:
                    conexion.sendall(
                        f"ERROR: Maximo {MAX_CARACTERES} caracteres.\n".encode()
                    )
                    continue

                # ELIMINAR MENSAJES ANTERIORES A 60 SEGUNDOS
                while historial and ahora - historial[0] >= 60:
                    historial.popleft()

                # COMPROBAR MENSAJES POR MINUTO
                if len(historial) >= MAX_MENSAJES_MINUTO:
                    bloqueado_hasta = ahora + SEGUNDOS_BLOQUEO
                    historial.clear()

                    conexion.sendall(
                        f"BLOQUEADO durante {SEGUNDOS_BLOQUEO} segundos.\n".encode()
                    )

                    print(f"Cliente bloqueado: {direccion}")
                    continue

                historial.append(ahora)

                print(f"{direccion}: {mensaje}")

                # REENVIAR A LOS DEMÁS CLIENTES
                with lock:
                    destinatarios = clientes.copy()

                for cliente in destinatarios:
                    if cliente != conexion:
                        try:
                            cliente.sendall(linea + b"\n")
                        except OSError:
                            pass

    except (ConnectionError, OSError):
        pass

    finally:
        with lock:
            if conexion in clientes:
                clientes.remove(conexion)

        conexion.close()
        print("Cliente desconectado:", direccion)


while True:
    conexion, direccion = servidor.accept()

    hilo = threading.Thread(
        target=atender_cliente,
        args=(conexion, direccion),
        daemon=True
    )

    hilo.start()