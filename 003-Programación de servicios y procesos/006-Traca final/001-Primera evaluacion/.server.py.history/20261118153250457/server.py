import asyncio
import json
import websockets

HOST = "0.0.0.0"
PORT = 8765

slaves = set()
master = None


async def handler(ws):
    global master

    role = None

    try:
        async for raw in ws:
            data = json.loads(raw)

            if data.get("type") == "register":
                role = data.get("role")

                if role == "master":
                    if master is not None:
                        await ws.close(
                            code=1008,
                            reason="Master already connected"
                        )
                        return

                    master = ws
                    print("MASTER connected")

                elif role == "slave":
                    slaves.add(ws)
                    print(
                        f"SLAVE connected. Total: {len(slaves)}"
                    )

                else:
                    await ws.close(code=1008)
                    return

            elif (
                role == "master"
                and ws is master
                and data.get("type") == "chat"
            ):
                message = data.get("message", "")

                print(f"MASTER: {message}")

                payload = json.dumps({
                    "type": "chat",
                    "message": message
                })

                if slaves:
                    await asyncio.gather(
                        *[
                            slave.send(payload)
                            for slave in list(slaves)
                        ],
                        return_exceptions=True
                    )

    except websockets.ConnectionClosed:
        pass

    finally:
        slaves.discard(ws)

        if ws is master:
            master = None
            print("MASTER disconnected")

        elif role == "slave":
            print(
                f"SLAVE disconnected. Total: {len(slaves)}"
            )


async def main():
    async with websockets.serve(
        handler,
        HOST,
        PORT
    ):
        print(f"Server listening on {HOST}:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
