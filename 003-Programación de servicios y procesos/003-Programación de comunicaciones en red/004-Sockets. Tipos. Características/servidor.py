import json
import socket
import threading
import time
from collections import deque

IP = "10.4.193.182"
PUERTO = 5000
MAX_MENSAJES_MINUTO = 10
MAX_CARACTERES = 200
SEGUNDOS_BLOQUEO = 60
MAX_LINEA_BYTES = 8192

clientes = {}  # socket -> {nombre, lock, historial, bloqueado_hasta}
lock = threading.RLock()


def enviar(conexion, paquete):
    datos = (json.dumps(paquete, ensure_ascii=False) + "\n").encode("utf-8")
    with lock:
        estado = clientes.get(conexion)
    if estado is None:
        return False
    try:
        with estado["lock"]:
            conexion.sendall(datos)
        return True
    except OSError:
        return False


def difundir(paquete, excluir=None):
    with lock:
        destinatarios = [c for c in clientes if c is not excluir]
    for c in destinatarios:
        enviar(c, paquete)


def atender_cliente(conexion, direccion):
    nombre = None
    buffer = b""
    try:
        conexion.settimeout(30)
        while True:
            datos = conexion.recv(4096)
            if not datos:
                break
            buffer += datos
            if len(buffer) > MAX_LINEA_BYTES:
                break
            while b"\n" in buffer:
                linea, buffer = buffer.split(b"\n", 1)
                if len(linea) > MAX_LINEA_BYTES:
                    return
                try:
                    paquete = json.loads(linea.decode("utf-8"))
                    if not isinstance(paquete, dict):
                        raise ValueError()
                except (UnicodeDecodeError, ValueError):
                    return

                if nombre is None:
                    if paquete.get("tipo") != "identificar":
                        return
                    candidato = paquete.get("nombre")
                    if not isinstance(candidato, str):
                        return
                    candidato = candidato.strip()
                    if not (1 <= len(candidato) <= 24) or any(ord(c) < 32 for c in candidato):
                        return
                    with lock:
                        ocupado = any(e["nombre"].casefold() == candidato.casefold() for e in clientes.values())
                        if not ocupado:
                            clientes[conexion] = {
                                "nombre": candidato,
                                "lock": threading.Lock(),
                                "historial": deque(),
                                "bloqueado_hasta": 0,
                            }
                    if ocupado:
                        conexion.sendall((json.dumps({"tipo": "error", "texto": "Nombre de usuario ocupado"}) + "\n").encode())
                        return
                    nombre = candidato
                    conexion.settimeout(None)
                    enviar(conexion, {"tipo": "identificado", "nombre": nombre})
                    difundir({"tipo": "sistema", "texto": f"{nombre} se ha conectado"})
                    print(f"Conectado: {nombre} ({direccion})")
                    continue

                if paquete.get("tipo") != "mensaje":
                    enviar(conexion, {"tipo": "error", "texto": "Tipo de mensaje desconocido"})
                    continue
                texto = paquete.get("texto")
                if not isinstance(texto, str) or not texto.strip():
                    enviar(conexion, {"tipo": "error", "texto": "Mensaje vacío o inválido"})
                    continue
                if len(texto) > MAX_CARACTERES:
                    enviar(conexion, {"tipo": "error", "texto": f"Máximo {MAX_CARACTERES} caracteres"})
                    continue
                if "\n" in texto or "\r" in texto:
                    enviar(conexion, {"tipo": "error", "texto": "No se permiten saltos de línea"})
                    continue
                ahora = time.monotonic()
                with lock:
                    estado = clientes[conexion]
                    if ahora < estado["bloqueado_hasta"]:
                        espera = int(estado["bloqueado_hasta"] - ahora) + 1
                        error = f"Bloqueado. Espera {espera} segundos"
                    else:
                        historial = estado["historial"]
                        while historial and ahora - historial[0] >= 60:
                            historial.popleft()
                        if len(historial) >= MAX_MENSAJES_MINUTO:
                            estado["bloqueado_hasta"] = ahora + SEGUNDOS_BLOQUEO
                            historial.clear()
                            error = f"Bloqueado durante {SEGUNDOS_BLOQUEO} segundos por exceso de mensajes"
                        else:
                            historial.append(ahora)
                            error = None
                if error:
                    enviar(conexion, {"tipo": "error", "texto": error})
                    continue
                difundir({"tipo": "mensaje", "usuario": nombre, "texto": texto})
                print(f"{nombre}: {texto}")
    except (OSError, ConnectionError):
        pass
    finally:
        with lock:
            clientes.pop(conexion, None)
        try:
            conexion.close()
        except OSError:
            pass
        if nombre:
            difundir({"tipo": "sistema", "texto": f"{nombre} se ha desconectado"})
            print(f"Desconectado: {nombre}")


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((IP, PUERTO))
    servidor.listen()
    print(f"Servidor escuchando en {IP}:{PUERTO}")
    try:
        while True:
            conexion, direccion = servidor.accept()
            threading.Thread(target=atender_cliente, args=(conexion, direccion), daemon=True).start()
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
