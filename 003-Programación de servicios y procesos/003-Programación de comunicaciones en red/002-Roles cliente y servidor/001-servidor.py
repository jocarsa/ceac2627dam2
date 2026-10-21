import socket

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.bind(("localhost", 5000))
servidor.listen(5)

print("Servidor esperando conexiones...")

while True:
    conexion, direccion = servidor.accept()
    print("Cliente conectado:", direccion)

    mensaje = conexion.recv(1024).decode("utf-8")
    print("Mensaje recibido:", mensaje)

    conexion.send("Hola desde el servidor".encode("utf-8"))

    conexion.close()