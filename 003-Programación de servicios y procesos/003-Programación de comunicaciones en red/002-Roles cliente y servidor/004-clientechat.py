import socket

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(("localhost", 5000))

while True:
    mensaje = input("Tú: ")
    cliente.send(mensaje.encode("utf-8"))

    if mensaje == "salir":
        break

    respuesta = cliente.recv(1024).decode("utf-8")

    if not respuesta or respuesta == "salir":
        break

    print("Servidor:", respuesta)

cliente.close()