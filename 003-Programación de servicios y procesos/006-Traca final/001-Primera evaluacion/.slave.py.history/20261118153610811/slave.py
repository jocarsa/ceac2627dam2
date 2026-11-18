
import asyncio
import json
import websockets

SERVER = "ws://jocarsa.com:8765"
TOKEN = "jocarsa-slave-2026"


async def main():
    while True:
        try:
            async with websockets.connect(SERVER) as ws:

                await ws.send(json.dumps({
                    "role": "slave",
                    "token": TOKEN
                }))

                response = json.loads(await ws.recv())

                if response.get("type") != "registered":
                    print("Registration failed")
                    return

                print(f"Connected to {SERVER}")

                async for raw in ws:
                    data = json.loads(raw)

                    if data.get("type") == "chat":
                        print(
                            f"MASTER > {data['message']}",
                            flush=True
                        )

        except (OSError, websockets.exceptions.ConnectionClosed) as e:
            print(f"Disconnected: {e}")
            print("Reconnecting in 3 seconds...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
