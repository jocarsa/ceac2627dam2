
import asyncio
import time
import websockets

from collections import defaultdict, deque

# CONFIGURACIÓN
IP = "10.4.193.182"
PUERTO = 5000

MAX_MENSAJES = 30
VENTANA = 60
TIEMPO_BLOQUEO = 600
MAX_TAMANO_MENSAJE = 4096

# ESTADO
clientes = set()
conexiones_ip = defaultdict(set)
mensajes_ip = defaultdict(deque)
bloqueados = {}

def obtener_ip(websocket):
    return websocket.remote_address[0]


def comprobar_limite(ip):
    ahora = time.monotonic()

    # ¿Está bloqueada?
    if ip in bloqueados:
        if ahora < bloqueados[ip]:
            return False

        del bloqueados[ip]

    # Eliminar mensajes antiguos
    historial = mensajes_ip[ip]

    while historial and ahora - historial[0] >= VENTANA:
        historial.popleft()

    # Comprobar límite
    if len(historial) >= MAX_MENSAJES:
        bloqueados[ip] = ahora + TIEMPO_BLOQUEO
        historial.clear()

        print(f"IP BLOQUEADA: {ip}")
        return False

    historial.append(ahora)
    return True


async def bloquear_conexiones(ip):
    conexiones = list(conexiones_ip.get(ip, set()))

    for conexion in conexiones:
        try:
            await conexion.close(
                code=1008,
                reason="Límite de mensajes superado"
            )
        except Exception:
            pass


async def atender(websocket):
    ip = obtener_ip(websocket)
    ahora = time.monotonic()

    # Rechazar IP bloqueada
    if bloqueados.get(ip, 0) > ahora:
        print(f"Conexión rechazada: {ip}")

        await websocket.close(
            code=1008,
            reason="IP bloqueada temporalmente"
        )
        return

    clientes.add(websocket)
    conexiones_ip[ip].add(websocket)

    print(f"Cliente conectado: {ip}")

    try:
        await websocket.send("Bienvenido al chat grupal")

        async for mensaje in websocket:

            # Comprobar si ya está bloqueada
            if bloqueados.get(ip, 0) > time.monotonic():
                await websocket.close(
                    code=1008,
                    reason="IP bloqueada"
                )
                break

            # Comprobar rate limiting
            if not comprobar_limite(ip):

                print(f"ABUSO DETECTADO: {ip}")

                await bloquear_conexiones(ip)
                break

            print(f"{ip}: {mensaje}")

            # Reenviar a todos los clientes
            destinatarios = list(clientes)

            resultados = await asyncio.gather(
                *(
                    cliente.send(mensaje)
                    for cliente in destinatarios
                ),
                return_exceptions=True
            )

            for cliente, resultado in zip(
                destinatarios, resultados
            ):
                if isinstance(resultado, Exception):
                    clientes.discard(cliente)

    except websockets.ConnectionClosed:
        pass

    finally:
        clientes.discard(websocket)
        conexiones_ip[ip].discard(websocket)

        if not conexiones_ip[ip]:
            del conexiones_ip[ip]

        print(f"Cliente desconectado: {ip}")


async def limpiar_registros():
    while True:
        await asyncio.sleep(60)

        ahora = time.monotonic()

        # Limpiar bloqueos caducados
        for ip, expiracion in list(bloqueados.items()):
            if ahora >= expiracion:
                del bloqueados[ip]
                print(f"IP DESBLOQUEADA: {ip}")

        # Limpiar historiales antiguos
        for ip, historial in list(mensajes_ip.items()):

            while historial and ahora - historial[0] >= VENTANA:
                historial.popleft()

            if not historial:
                del mensajes_ip[ip]


async def main():
    async with websockets.serve(
        atender,
        IP,
        PUERTO,
        max_size=MAX_TAMANO_MENSAJE,
        max_queue=16,
        open_timeout=5
    ):
        print(f"Servidor escuchando en ws://{IP}:{PUERTO}")
        print(f"Límite: {MAX_MENSAJES} mensajes por minuto")
        print(f"Bloqueo: {TIEMPO_BLOQUEO} segundos")

        await limpiar_registros()


asyncio.run(main())
