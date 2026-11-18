
import asyncio
import json
import websockets

SERVER = "ws://127.0.0.1:8765"


async def main():
    while True:
        try:
            async with websockets.connect(SERVER) as ws:

                await ws.send(json.dumps({
                    "type": "register",
                    "role": "slave"
                }))

                print("Connected as SLAVE")

                async for raw in ws:
                    data = json.loads(raw)

                    if data.get("type") == "chat":
                        print(
                            f"MASTER > {data['message']}",
                            flush=True
                        )

        except (
            OSError,
            websockets.ConnectionClosed
        ):
            print("Disconnected. Reconnecting...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
