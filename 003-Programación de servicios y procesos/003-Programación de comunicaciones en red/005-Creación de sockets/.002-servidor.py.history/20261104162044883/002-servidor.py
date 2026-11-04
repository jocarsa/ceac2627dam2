import asyncio
import websockets

async def atender(websocket):
    await websocket.send("Hello")

async def main():
    async with websockets.serve(atender, "localhost", 5000):
        await asyncio.Future()

asyncio.run(main())