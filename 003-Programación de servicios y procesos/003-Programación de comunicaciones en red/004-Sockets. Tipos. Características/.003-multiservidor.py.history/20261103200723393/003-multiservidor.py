
import socket
import threading

IP = "10.4.193.182"
PUERTO = 5000

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((IP, PUERTO))
servidor.listen()

clientes = []
lock = threading.Lock()

print(f"Servidor escuchando en {IP}:{PUERTO}")

def atender_cliente(conexion, direccion):
    print("Cliente conectado:", direccion)

    with lock:
        clientes.append(conexion)

    try:
        while True:
            datos = conexion.recv(1024)

            if not datos:
                break

            mensaje = datos.decode("utf-8")
            print(f"{direccion}: {mensaje}")

            with lock:
                destinatarios = clientes.copy()

            for cliente in destinatarios:
                if cliente != conexion:
                    try:
                        cliente.sendall(datos)
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
