import asyncio
import websockets

clientes = set()

async def atender(websocket):

    clientes.add(websocket)
    print("Cliente conectado. Total:", len(clientes))

    try:
        await websocket.send("Bienvenido al chat grupal")

        async for mensaje in websocket:
            print("Cliente:", mensaje)

            # Reenviar a todos los clientes
            for cliente in clientes.copy():
                try:
                    await cliente.send(mensaje)
                except websockets.ConnectionClosed:
                    clientes.discard(cliente)

    finally:
        clientes.discard(websocket)
        print("Cliente desconectado. Total:", len(clientes))


async def main():
    async with websockets.serve(
        atender,
        "10.4.193.182",
        5000
    ):
        print("Servidor escuchando en ws://10.4.193.182:5000")
        await asyncio.Future()


asyncio.run(main())