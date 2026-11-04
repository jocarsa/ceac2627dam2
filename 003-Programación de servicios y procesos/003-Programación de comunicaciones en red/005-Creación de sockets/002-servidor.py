import asyncio
import websockets

async def atender(websocket):
    await websocket.send("Hello")

    async for mensaje in websocket:
        print("Cliente:", mensaje)
        await websocket.send("Servidor recibió: " + mensaje)

async def main():
    async with websockets.serve(atender, "10.4.193.182", 5000):
        print("Servidor escuchando en ws://10.4.193.182:5000")
        await asyncio.Future()

asyncio.run(main())