
import socket
import threading

IP = "10.4.193.182"
PUERTO = 5000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((IP, PUERTO))

nombre = input("Tu nombre: ")

def recibir():
    while True:
        try:
            mensaje = cliente.recv(1024).decode("utf-8")
            if not mensaje:
                break
            print("\n" + mensaje)
        except OSError:
            break

    print("Desconectado del servidor.")

threading.Thread(target=recibir, daemon=True).start()

while True:
    mensaje = input()

    if mensaje == "salir":
        break

    try:
        cliente.sendall(
            f"{nombre}: {mensaje}".encode("utf-8")
        )
    except OSError:
        break

cliente.close()
