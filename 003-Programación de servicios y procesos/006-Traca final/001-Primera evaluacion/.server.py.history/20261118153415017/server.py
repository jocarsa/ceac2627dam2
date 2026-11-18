
#!/usr/bin/env python3

import asyncio
import json
import os
import hmac
import logging

import websockets
from websockets.exceptions import ConnectionClosed

HOST = "127.0.0.1"
PORT = 8765

MASTER_TOKEN = os.environ["JOCARSA_MASTER_TOKEN"]
SLAVE_TOKEN = os.environ["JOCARSA_SLAVE_TOKEN"]

slaves = set()
master = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)


async def send_to_slaves(payload):
    if not slaves:
        return

    message = json.dumps(payload, ensure_ascii=False)

    results = await asyncio.gather(
        *(slave.send(message) for slave in list(slaves)),
        return_exceptions=True
    )

    for result in results:
        if isinstance(result, Exception):
            logging.warning("Slave delivery failed: %s", result)


async def handler(ws):
    global master

    role = None

    try:
        raw = await asyncio.wait_for(ws.recv(), timeout=10)
        data = json.loads(raw)

        if not isinstance(data, dict):
            await ws.close(1008, "Invalid registration")
            return

        role = data.get("role")
        token = data.get("token")

        if not isinstance(token, str):
            await ws.close(1008, "Authentication required")
            return

        if role == "master":
            if not hmac.compare_digest(token, MASTER_TOKEN):
                await ws.close(1008, "Unauthorized")
                return

            if master is not None:
                await ws.close(1008, "Master already connected")
                return

            master = ws
            logging.info("MASTER connected")

        elif role == "slave":
            if not hmac.compare_digest(token, SLAVE_TOKEN):
                await ws.close(1008, "Unauthorized")
                return

            slaves.add(ws)
            logging.info(
                "SLAVE connected | Total: %d",
                len(slaves)
            )

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
            except json.JSONDecodeError:
                continue

            if not isinstance(data, dict):
                continue

            if role != "master":
                continue

            if data.get("type") == "chat":
                message = data.get("message")

                if not isinstance(message, str):
                    continue

                logging.info("MASTER: %s", message)

                await send_to_slaves({
                    "type": "chat",
                    "message": message
                })

    except (
        ConnectionClosed,
        asyncio.TimeoutError,
        json.JSONDecodeError
    ):
        pass

    finally:
        if ws is master:
            master = None
            logging.info("MASTER disconnected")

        if ws in slaves:
            slaves.discard(ws)
            logging.info(
                "SLAVE disconnected | Total: %d",
                len(slaves)
            )


async def main():
    if not MASTER_TOKEN or not SLAVE_TOKEN:
        raise RuntimeError("Authentication tokens cannot be empty")

    async with websockets.serve(
        handler,
        HOST,
        PORT,
        ping_interval=20,
        ping_timeout=20,
        max_size=1024 * 1024
    ):
        logging.info(
            "JOCARSA WebSocket server on %s:%d",
            HOST,
            PORT
        )

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
