
import asyncio
import json
import hmac
import websockets

HOST = "0.0.0.0"
PORT = 8765

MASTER_TOKEN = "jocarsa-master-2026"
SLAVE_TOKEN = "jocarsa-slave-2026"

slaves = set()
master = None


async def handler(ws):
    global master

    role = None

    try:
        data = json.loads(
            await asyncio.wait_for(ws.recv(), timeout=10)
        )

        role = data.get("role")
        token = data.get("token")

        if role == "master":
            if not isinstance(token, str) or not hmac.compare_digest(
                token, MASTER_TOKEN
            ):
                await ws.close(1008, "Invalid master token")
                return

            if master is not None:
                await ws.close(1008, "Master already connected")
                return

            master = ws
            print("MASTER connected")

        elif role == "slave":
            if not isinstance(token, str) or not hmac.compare_digest(
                token, SLAVE_TOKEN
            ):
                await ws.close(1008, "Invalid slave token")
                return

            slaves.add(ws)
            print(f"SLAVE connected | Total: {len(slaves)}")

        else:
            await ws.close(1008, "Invalid role")
            return

        await ws.send(json.dumps({
            "type": "registered",
            "role": role
        }))

        async for raw in ws:
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(data, dict):
                continue

            if role == "master" and data.get("type") == "chat":
                message = data.get("message")

                if not isinstance(message, str):
                    continue

                print(f"MASTER > {message}")

                payload = json.dumps({
                    "type": "chat",
                    "message": message
                }, ensure_ascii=False)

                if slaves:
                    results = await asyncio.gather(
                        *(slave.send(payload) for slave in list(slaves)),
                        return_exceptions=True
                    )

                    for result in results:
                        if isinstance(result, Exception):
                            print(f"Delivery error: {result}")

    except (
        websockets.exceptions.ConnectionClosed,
        asyncio.TimeoutError,
        json.JSONDecodeError,
        TypeError
    ):
        pass

    finally:
        slaves.discard(ws)

        if ws is master:
            master = None
            print("MASTER disconnected")

        elif role == "slave":
            print(f"SLAVE disconnected | Total: {len(slaves)}")


async def main():
    async with websockets.serve(
        handler,
        HOST,
        PORT,
        ping_interval=20,
        ping_timeout=20
    ):
        print(f"Server listening on ws://{HOST}:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
