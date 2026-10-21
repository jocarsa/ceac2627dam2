import socket

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect(("localhost", 5000))

cliente.send("Hola desde el cliente".encode("utf-8"))

respuesta = cliente.recv(1024).decode("utf-8")

print("Respuesta:", respuesta)

cliente.close()