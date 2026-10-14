import socket

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind(("localhost", 5000))
servidor.listen(1)

print("Esperando cliente...")
conexion, direccion = servidor.accept()
print("Cliente conectado:", direccion)

while True:
    mensaje = conexion.recv(1024).decode("utf-8")

    if not mensaje or mensaje == "salir":
        break

    print("Cliente:", mensaje)

    respuesta = input("Servidor: ")
    conexion.send(respuesta.encode("utf-8"))

    if respuesta == "salir":
        break

conexion.close()
servidor.close()