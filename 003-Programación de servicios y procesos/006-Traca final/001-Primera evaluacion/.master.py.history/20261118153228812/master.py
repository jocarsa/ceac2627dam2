
import asyncio
import json
import websockets

SERVER = "ws://127.0.0.1:8765"


async def main():
    async with websockets.connect(SERVER) as ws:

        await ws.send(json.dumps({
            "type": "register",
            "role": "master"
        }))

        print("Connected as MASTER")
        print("Type messages. /exit to quit.")

        while True:
            message = await asyncio.to_thread(
                input, "MASTER > "
            )

            if message.strip() == "/exit":
                break

            await ws.send(json.dumps({
                "type": "chat",
                "message": message
            }))


if __name__ == "__main__":
    asyncio.run(main())
