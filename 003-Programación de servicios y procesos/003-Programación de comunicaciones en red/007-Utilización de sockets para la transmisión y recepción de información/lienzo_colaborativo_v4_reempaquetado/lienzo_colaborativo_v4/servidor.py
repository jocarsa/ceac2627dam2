import asyncio, json, os, sqlite3, time, uuid, ipaddress
from pathlib import Path
from websockets.asyncio.server import serve

HOST=os.getenv('HOST','0.0.0.0'); PORT=int(os.getenv('PORT','8765'))
DB=Path(__file__).with_name('vida.sqlite3')
WIDTH,HEIGHT=1920,1080
CELL=int(os.getenv('CELL_SIZE','10'))
assert CELL>=2 and WIDTH%CELL==0 and HEIGHT%CELL==0
COLS,ROWS=WIDTH//CELL,HEIGHT//CELL
TICK=float(os.getenv('TICK_SECONDS','0.25'))
ADMIN_IPS={s.strip() for s in os.getenv('ADMIN_IPS','10.4.193.182,127.0.0.1,::1').split(',')}
clients={}; grid=set(); generation=0; running=True; lock=asyncio.Lock()

def dbconn():
    db=sqlite3.connect(DB,timeout=10)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('CREATE TABLE IF NOT EXISTS bans (name TEXT PRIMARY KEY, display TEXT, admin TEXT, created REAL)')
    db.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), generation INTEGER, cells TEXT)')
    db.commit();return db

def norm(s):return s.strip().casefold()
def banned(name):
    with dbconn() as db:return bool(db.execute('SELECT 1 FROM bans WHERE name=?',(norm(name),)).fetchone())
def bans():
    with dbconn() as db:return [r[0] for r in db.execute('SELECT display FROM bans ORDER BY created DESC')]
def setban(name,admin):
    with dbconn() as db:db.execute('INSERT OR REPLACE INTO bans VALUES(?,?,?,?)',(norm(name),name,admin,time.time()))
def unban(name):
    with dbconn() as db:db.execute('DELETE FROM bans WHERE name=?',(norm(name),))
def load():
    with dbconn() as db:
        row=db.execute('SELECT generation,cells FROM state WHERE id=1').fetchone()
        if row:return int(row[0]),set(int(x) for x in json.loads(row[1]) if type(x)==int and 0<=x<COLS*ROWS)
    return 0,set()
def save(gen,cells):
    with dbconn() as db:db.execute('INSERT OR REPLACE INTO state VALUES(1,?,?)',(gen,json.dumps(sorted(cells))))

def evolve(live):
    counts={}
    for v in live:
        x,y=v%COLS,v//COLS
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dx==0 and dy==0:continue
                nx,ny=x+dx,y+dy
                if 0<=nx<COLS and 0<=ny<ROWS:
                    k=ny*COLS+nx;counts[k]=counts.get(k,0)+1
    return {k for k,n in counts.items() if n==3 or (n==2 and k in live)}

async def send(ws,data):
    await ws.send(json.dumps(data,separators=(',',':'),ensure_ascii=False))
async def broadcast(data):
    if clients:await asyncio.gather(*(send(ws,data) for ws in list(clients)),return_exceptions=True)

async def handler(ws):
    global grid,generation,running
    uid=uuid.uuid4().hex[:12];name=None
    ip=ws.remote_address[0] if ws.remote_address else ''
    try:ip=str(ipaddress.ip_address(ip).ipv4_mapped or ipaddress.ip_address(ip))
    except ValueError:pass
    admin=ip in ADMIN_IPS
    last_draw=0;last_cursor=0
    try:
        async for raw in ws:
            if not isinstance(raw,str) or len(raw)>30000:continue
            try:m=json.loads(raw)
            except (ValueError,TypeError):continue
            if not isinstance(m,dict):continue
            typ=m.get('type')
            if name is None:
                if typ!='login':continue
                candidate=m.get('name')
                if not isinstance(candidate,str):continue
                candidate=candidate.strip()
                if not 1<=len(candidate)<=24 or any(ord(c)<32 for c in candidate):
                    await send(ws,{'type':'error','message':'Nombre inválido'});continue
                if await asyncio.to_thread(banned,candidate):
                    await send(ws,{'type':'banned','message':'Usuario bloqueado'});await ws.close(code=1008);return
                if any(norm(u['name'])==norm(candidate) for u in clients.values()):
                    await send(ws,{'type':'error','message':'Nombre en uso'});continue
                name=candidate
                async with lock:
                    clients[ws]={'id':uid,'name':name,'admin':admin}
                    snapshot={'type':'init','id':uid,'name':name,'admin':admin,'users':list(clients.values()),'bans':await asyncio.to_thread(bans) if admin else [],'cells':sorted(grid),'generation':generation,'running':running,'cols':COLS,'rows':ROWS,'cellSize':CELL}
                await send(ws,snapshot)
                await broadcast({'type':'users','users':list(clients.values())})
                continue
            if typ=='cursor':
                now=time.monotonic()
                if now-last_cursor<.05:continue
                last_cursor=now
                x,y=m.get('x'),m.get('y')
                if type(x)==int and type(y)==int and 0<=x<COLS and 0<=y<ROWS:
                    await broadcast({'type':'cursor','id':uid,'x':x,'y':y})
            elif typ=='paint':
                now=time.monotonic()
                if now-last_draw<.015:continue
                last_draw=now
                cells=m.get('cells');mode=m.get('mode')
                if not isinstance(cells,list) or len(cells)>500 or mode not in ('alive','dead'):continue
                valid={v for v in cells if type(v)==int and 0<=v<COLS*ROWS}
                if not valid:continue
                async with lock:
                    if mode=='alive':grid.update(valid)
                    else:grid.difference_update(valid)
                    gen=generation
                await broadcast({'type':'paint','cells':sorted(valid),'mode':mode,'id':uid,'generation':gen})
            elif typ in ('ban','unban'):
                if not admin:continue
                target=m.get('name')
                if not isinstance(target,str) or not 1<=len(target.strip())<=24:continue
                target=target.strip()
                if typ=='ban':
                    if norm(target)==norm(name) or any(u['admin'] and norm(u['name'])==norm(target) for u in clients.values()):continue
                    await asyncio.to_thread(setban,target,name)
                    for peer,u in list(clients.items()):
                        if norm(u['name'])==norm(target):
                            await send(peer,{'type':'banned','message':'Has sido baneado'});await peer.close(code=1008)
                else:await asyncio.to_thread(unban,target)
                await send(ws,{'type':'bans','names':await asyncio.to_thread(bans)})
            elif typ in ('pause','resume','step','clear'):
                if not admin:continue
                async with lock:
                    if typ=='pause':running=False
                    elif typ=='resume':running=True
                    elif typ=='clear':grid.clear();generation=0
                    elif typ=='step':grid=evolve(grid);generation+=1
                    msg={'type':'state','cells':sorted(grid),'generation':generation,'running':running}
                await broadcast(msg)
    finally:
        clients.pop(ws,None)
        if name:
            await broadcast({'type':'users','users':list(clients.values())})
            await broadcast({'type':'leave','id':uid})

async def simulation():
    global grid,generation
    ticks=0
    while True:
        await asyncio.sleep(max(.05,TICK))
        async with lock:
            if not running:continue
            grid=evolve(grid);generation+=1
            msg={'type':'state','cells':sorted(grid),'generation':generation,'running':running}
            ticks+=1
            if ticks%20==0:
                await asyncio.to_thread(save,generation,grid.copy())
        await broadcast(msg)

async def main():
    global grid,generation
    generation,grid=await asyncio.to_thread(load)
    print(f'Juego de la Vida: ws://{HOST}:{PORT} | {COLS}x{ROWS} celdas | intervalo {TICK}s')
    async with serve(handler,HOST,PORT,max_size=30000,ping_interval=20):
        task=asyncio.create_task(simulation())
        try:await asyncio.Future()
        finally:task.cancel();await asyncio.to_thread(save,generation,grid)

if __name__=='__main__':asyncio.run(main())
