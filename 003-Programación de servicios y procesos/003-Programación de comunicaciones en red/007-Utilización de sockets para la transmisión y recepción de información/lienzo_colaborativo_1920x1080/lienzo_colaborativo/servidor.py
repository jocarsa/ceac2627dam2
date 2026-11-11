import asyncio
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path

from websockets.asyncio.server import serve

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8765'))
DB = Path(__file__).with_name('lienzo.sqlite3')
WIDTH, HEIGHT = 1920, 1080
MAX_POINTS = 5000
clients = {}
active = {}


def connect_db():
    db = sqlite3.connect(DB)
    db.execute('CREATE TABLE IF NOT EXISTS strokes (id TEXT PRIMARY KEY, user_id TEXT NOT NULL, data TEXT NOT NULL, created REAL NOT NULL)')
    db.commit()
    return db


def history():
    with connect_db() as db:
        return [json.loads(row[0]) for row in db.execute('SELECT data FROM strokes ORDER BY created, rowid')]


def save(stroke):
    with connect_db() as db:
        db.execute('INSERT INTO strokes VALUES (?,?,?,?)', (stroke['id'], stroke['user'], json.dumps(stroke, separators=(',', ':')), time.time()))


def point(p):
    if not isinstance(p, list) or len(p) != 2:
        return None
    try:
        x, y = float(p[0]), float(p[1])
        if not (0 <= x <= WIDTH and 0 <= y <= HEIGHT):
            return None
        return [round(x, 2), round(y, 2)]
    except (ValueError, TypeError, OverflowError):
        return None


async def broadcast(msg, exclude=None):
    data = json.dumps(msg, ensure_ascii=False, separators=(',', ':'))
    for ws in list(clients):
        if ws != exclude:
            try:
                await ws.send(data)
            except Exception:
                pass


async def handler(ws):
    uid = uuid.uuid4().hex[:12]
    clients[ws] = uid
    try:
        await ws.send(json.dumps({'type': 'init', 'id': uid, 'width': WIDTH, 'height': HEIGHT, 'strokes': history(), 'online': len(clients)}))
        await broadcast({'type': 'online', 'count': len(clients)})
        async for raw in ws:
            if len(raw) > 16000:
                continue
            try:
                msg = json.loads(raw)
            except (ValueError, TypeError):
                continue
            typ = msg.get('type') if isinstance(msg, dict) else None
            if typ == 'begin':
                p = point(msg.get('point'))
                color = msg.get('color')
                tool = msg.get('tool')
                size = msg.get('size')
                sid = msg.get('id')
                if not p or not isinstance(sid, str) or len(sid) > 80 or not isinstance(color, str) or len(color) != 7 or color[0] != '#' or any(c not in '0123456789abcdefABCDEF' for c in color[1:]) or tool not in ('brush', 'eraser', 'line', 'rect', 'ellipse') or not isinstance(size, (int, float)) or not 1 <= size <= 100:
                    continue
                key = (uid, sid)
                if len([k for k in active if k[0] == uid]) > 2:
                    continue
                stroke = {'id': uid + '-' + sid, 'user': uid, 'tool': tool, 'color': color, 'size': int(size), 'points': [p]}
                active[key] = stroke
                await broadcast({'type': 'begin', 'stroke': stroke}, ws)
            elif typ == 'point':
                sid = msg.get('id')
                p = point(msg.get('point'))
                stroke = active.get((uid, sid)) if isinstance(sid, str) else None
                if stroke and p and len(stroke['points']) < MAX_POINTS:
                    stroke['points'].append(p)
                    await broadcast({'type': 'point', 'id': stroke['id'], 'point': p}, ws)
            elif typ == 'end':
                sid = msg.get('id')
                stroke = active.pop((uid, sid), None) if isinstance(sid, str) else None
                if stroke:
                    save(stroke)
                    await broadcast({'type': 'end', 'id': stroke['id']}, ws)
            elif typ == 'undo':
                with connect_db() as db:
                    row = db.execute('SELECT id FROM strokes WHERE user_id=? ORDER BY created DESC, rowid DESC LIMIT 1', (uid,)).fetchone()
                    if row:
                        db.execute('DELETE FROM strokes WHERE id=?', (row[0],))
                if row:
                    await broadcast({'type': 'remove', 'id': row[0]})
    finally:
        clients.pop(ws, None)
        for key in list(active):
            if key[0] == uid:
                active.pop(key, None)
        await broadcast({'type': 'online', 'count': len(clients)})


async def main():
    connect_db().close()
    print(f'Lienzo colaborativo WebSocket: ws://{HOST}:{PORT}')
    async with serve(handler, HOST, PORT, max_size=16000, ping_interval=20):
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
