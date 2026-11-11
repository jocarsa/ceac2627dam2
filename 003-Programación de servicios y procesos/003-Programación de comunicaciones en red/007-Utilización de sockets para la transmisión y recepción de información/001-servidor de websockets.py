import asyncio
import websockets

clientes = set()                                      # Clientes conectados

async def manejar_cliente(websocket):                 # Gestiona cada conexión

    clientes.add(websocket)                           # Registra el cliente
    print("Cliente conectado:", websocket.remote_address)

    try:
        async for mensaje in websocket:                # Escucha mensajes
            print("Mensaje recibido:", mensaje)

            for cliente in clientes.copy():            # Recorre clientes
                try:
                    await cliente.send(mensaje)         # Reenvía mensaje
                except websockets.ConnectionClosed:
                    clientes.discard(cliente)

    except websockets.ConnectionClosed:
        pass

    finally:
        clientes.discard(websocket)                     # Elimina cliente
        print("Cliente desconectado")


async def main():

    async with websockets.serve(
        manejar_cliente,
        "0.0.0.0",
        8765
    ):
        print("Servidor WebSocket iniciado en puerto 8765")
        await asyncio.Future()                         # Mantiene servidor activo


asyncio.run(main())