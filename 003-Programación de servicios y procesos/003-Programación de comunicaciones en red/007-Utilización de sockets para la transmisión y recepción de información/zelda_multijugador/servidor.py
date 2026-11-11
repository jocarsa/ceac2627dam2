import asyncio
import json
import random
import uuid
import websockets

HOST = '0.0.0.0'
PORT = 8765
WORLD = [
'########################',
'#....T.............T...#',
'#..TTT.....~~~~...TT...#',
'#..........~~~~........#',
'#.....####.............#',
'#.....#..#......TT.....#',
'#.....#..#.............#',
'#.....####.....~~~~....#',
'#..............~~~~....#',
'#..TT..................#',
'#...........TT.........#',
'#....~~~~..............#',
'#....~~~~.......TT.....#',
'#......................#',
'#.......TT.............#',
'#......................#',
'########################',
]
players = {}
connections = {}
COLORS = ['#f97373', '#60a5fa', '#fbbf24', '#c084fc', '#34d399', '#fb923c']

def valid(x, y):
    tx, ty = int(x), int(y)
    return 0 <= ty < len(WORLD) and 0 <= tx < len(WORLD[0]) and WORLD[ty][tx] == '.'

def spawn():
    cells = [(x + .5, y + .5) for y, row in enumerate(WORLD) for x, tile in enumerate(row) if tile == '.']
    return random.choice(cells)

async def broadcast():
    if not connections:
        return
    data = json.dumps({'type': 'state', 'players': list(players.values())}, ensure_ascii=False)
    await asyncio.gather(*(ws.send(data) for ws in list(connections.values())), return_exceptions=True)

async def handler(ws):
    pid = uuid.uuid4().hex[:8]
    x, y = spawn()
    players[pid] = {'id': pid, 'name': 'Aventurero', 'x': x, 'y': y, 'color': random.choice(COLORS), 'direction': 'down'}
    connections[pid] = ws
    await ws.send(json.dumps({'type': 'welcome', 'id': pid, 'map': WORLD}))
    await broadcast()
    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if not isinstance(msg, dict):
                continue
            p = players[pid]
            if msg.get('type') == 'name':
                p['name'] = str(msg.get('name', 'Aventurero')).strip()[:18] or 'Aventurero'
                await broadcast()
            elif msg.get('type') == 'move':
                direction = msg.get('direction')
                if direction not in ('up', 'down', 'left', 'right'):
                    continue
                dx, dy = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}[direction]
                step = .13
                nx, ny = p['x'] + dx * step, p['y'] + dy * step
                if valid(nx, p['y']):
                    p['x'] = nx
                if valid(p['x'], ny):
                    p['y'] = ny
                p['direction'] = direction
                await broadcast()
    except websockets.ConnectionClosed:
        pass
    finally:
        connections.pop(pid, None)
        players.pop(pid, None)
        await broadcast()

async def main():
    async with websockets.serve(handler, HOST, PORT, max_size=2048):
        print(f'WebSocket escuchando en ws://{HOST}:{PORT}')
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
