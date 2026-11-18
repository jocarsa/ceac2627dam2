
import asyncio
import json
import websockets

SERVER = "ws://jocarsa.com:8765"
TOKEN = "jocarsa-master-2026"


async def main():
    while True:
        try:
            async with websockets.connect(SERVER) as ws:

                await ws.send(json.dumps({
                    "role": "master",
                    "token": TOKEN
                }))

                response = json.loads(await ws.recv())

                if response.get("type") != "registered":
                    print("Registration failed")
                    return

                print(f"Connected to {SERVER}")
                print("Type /exit to quit")

                while True:
                    message = await asyncio.to_thread(
                        input, "MASTER > "
                    )

                    if message.strip() == "/exit":
                        return

                    if message.strip():
                        await ws.send(json.dumps({
                            "type": "chat",
                            "message": message
                        }, ensure_ascii=False))

        except (OSError, websockets.exceptions.ConnectionClosed) as e:
            print(f"Disconnected: {e}")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
