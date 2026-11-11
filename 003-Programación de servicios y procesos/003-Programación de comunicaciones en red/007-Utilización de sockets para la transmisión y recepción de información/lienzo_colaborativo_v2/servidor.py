import asyncio, json, os, sqlite3, time, uuid, re, math
from pathlib import Path
from websockets.asyncio.server import serve

HOST=os.getenv('HOST','0.0.0.0'); PORT=int(os.getenv('PORT','8765'))
DB=Path(__file__).with_name('lienzo.sqlite3'); WIDTH=1920; HEIGHT=1080
clients={}; active={}; db_lock=asyncio.Lock()

def database():
    db=sqlite3.connect(DB,timeout=20)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('CREATE TABLE IF NOT EXISTS strokes (id TEXT PRIMARY KEY,user_id TEXT NOT NULL,data TEXT NOT NULL,created REAL NOT NULL)')
    db.commit(); return db

def load():
    with database() as db: return [json.loads(x[0]) for x in db.execute('SELECT data FROM strokes ORDER BY created,rowid')]

def point(p):
    if not isinstance(p,list) or len(p)!=2:return None
    try:
        x,y=map(float,p)
        if math.isfinite(x) and math.isfinite(y) and 0<=x<=WIDTH and 0<=y<=HEIGHT:return [round(x,2),round(y,2)]
    except (ValueError,TypeError,OverflowError):pass
    return None

async def broadcast(msg,exclude=None):
    raw=json.dumps(msg,ensure_ascii=False,separators=(',',':'))
    peers=[ws for ws in clients if ws!=exclude]
    if peers: await asyncio.gather(*(ws.send(raw) for ws in peers),return_exceptions=True)

async def handler(ws):
    uid=uuid.uuid4().hex[:12]; username=None; last_cursor=0; last_begin=0
    try:
        async for raw in ws:
            if not isinstance(raw,str) or len(raw)>16000:continue
            try: m=json.loads(raw)
            except (ValueError,TypeError):continue
            if not isinstance(m,dict):continue
            typ=m.get('type')
            if username is None:
                if typ!='login':continue
                name=m.get('name','')
                if not isinstance(name,str):continue
                name=name.strip()
                if not 1<=len(name)<=24 or any(ord(c)<32 for c in name):
                    await ws.send(json.dumps({'type':'error','message':'Nombre inválido (1-24 caracteres)'}));continue
                username=name; clients[ws]={'id':uid,'name':username}
                await ws.send(json.dumps({'type':'init','id':uid,'name':username,'width':WIDTH,'height':HEIGHT,'strokes':await asyncio.to_thread(load),'users':list(clients.values())},ensure_ascii=False))
                await broadcast({'type':'join','user':clients[ws]},ws)
                continue
            if typ=='cursor':
                now=time.monotonic()
                if now-last_cursor<1/25:continue
                last_cursor=now; p=point(m.get('point'))
                if p:await broadcast({'type':'cursor','id':uid,'point':p},ws)
            elif typ=='begin':
                p=point(m.get('point'));color=m.get('color');tool=m.get('tool');size=m.get('size');sid=m.get('id');now=time.monotonic()
                if now-last_begin<.025:continue
                if not p or not isinstance(sid,str) or not 1<=len(sid)<=80 or not re.fullmatch(r'#[0-9a-fA-F]{6}',str(color)) or tool not in ('brush','eraser','line','rect','ellipse') or type(size) not in (int,float) or not math.isfinite(size) or not 1<=size<=100:continue
                if sum(k[0]==uid for k in active)>=2:continue
                last_begin=now
                stroke={'id':uid+'-'+sid,'user':uid,'name':username,'tool':tool,'color':color,'size':int(size),'points':[p]}
                active[(uid,sid)]=stroke;await broadcast({'type':'begin','stroke':stroke},ws)
            elif typ=='point':
                sid=m.get('id');p=point(m.get('point'));stroke=active.get((uid,sid)) if isinstance(sid,str) else None
                if stroke and p and len(stroke['points'])<5000:
                    if stroke['tool'] in ('brush','eraser'):stroke['points'].append(p)
                    else:stroke['points']=stroke['points'][:1]+[p]
                    await broadcast({'type':'point','id':stroke['id'],'point':p},ws)
            elif typ=='end':
                sid=m.get('id');stroke=active.pop((uid,sid),None) if isinstance(sid,str) else None
                if stroke:
                    async with db_lock:
                        def persist():
                            with database() as db:db.execute('INSERT INTO strokes VALUES (?,?,?,?)',(stroke['id'],uid,json.dumps(stroke,separators=(',',':')),time.time()))
                        await asyncio.to_thread(persist)
                    await broadcast({'type':'end','id':stroke['id']},ws)
            elif typ=='undo':
                async with db_lock:
                    def undo():
                        with database() as db:
                            row=db.execute('SELECT id FROM strokes WHERE user_id=? ORDER BY created DESC,rowid DESC LIMIT 1',(uid,)).fetchone()
                            if row:db.execute('DELETE FROM strokes WHERE id=?',(row[0],))
                            return row[0] if row else None
                    removed=await asyncio.to_thread(undo)
                if removed:await broadcast({'type':'remove','id':removed})
    finally:
        clients.pop(ws,None)
        for k in list(active):
            if k[0]==uid:active.pop(k,None)
        if username:await broadcast({'type':'leave','id':uid})

async def main():
    database().close();print(f'WebSocket ws://{HOST}:{PORT} (asyncio, SQLite WAL)')
    async with serve(handler,HOST,PORT,max_size=16000,ping_interval=20):await asyncio.Future()

if __name__=='__main__':asyncio.run(main())
