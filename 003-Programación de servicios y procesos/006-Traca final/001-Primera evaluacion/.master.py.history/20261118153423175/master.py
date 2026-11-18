
#!/usr/bin/env python3

import asyncio
import json
import os

import websockets

SERVER = "wss://jocarsa.com/ws/"
TOKEN = os.environ["JOCARSA_MASTER_TOKEN"]


async def main():
    while True:
        try:
            print(f"Connecting to {SERVER}...")

            async with websockets.connect(
                SERVER,
                ping_interval=20,
                ping_timeout=20
            ) as ws:

                await ws.send(json.dumps({
                    "role": "master",
                    "token": TOKEN
                }))

                response = json.loads(await ws.recv())

                if response.get("type") != "registered":
                    raise RuntimeError("Registration failed")

                print("Connected as MASTER")
                print("Type /exit to quit")

                while True:
                    message = await asyncio.to_thread(
                        input,
                        "MASTER > "
                    )

                    if message.strip() == "/exit":
                        return

                    if not message.strip():
                        continue

                    await ws.send(json.dumps({
                        "type": "chat",
                        "message": message
                    }, ensure_ascii=False))

        except (OSError, websockets.exceptions.ConnectionClosed) as e:
            print(f"Disconnected: {e}")
            print("Reconnecting in 3 seconds...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
