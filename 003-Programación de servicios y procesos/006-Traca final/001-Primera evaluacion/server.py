#!/usr/bin/env python3
"""Broker persistente con prefetch, planificación inmediata y monitor HTTP."""
import argparse,asyncio,json,sqlite3,time,hmac
import websockets
p=argparse.ArgumentParser()
p.add_argument('--host',default='0.0.0.0');p.add_argument('--port',type=int,default=8765)
p.add_argument('--monitor-port',type=int,default=8766);p.add_argument('--db',default='cola.sqlite3')
p.add_argument('--lease',type=int,default=900);p.add_argument('--max-attempts',type=int,default=5)
a=p.parse_args()
MASTER='yhVHs0O8ZEZZkR_stCNGjY7OG-THoJsadab18oounmXV64Bn'
SLAVE='y3sSimNlzDr7UNEZ6gYXlwsP-na5lrCeUwyffKQ4C0sirfwv'
MONITOR='MGDxjirs5hKARWquLLsics0EzGE5x7fqyHUwyxtlAimFIduy'
db=sqlite3.connect(a.db);db.row_factory=sqlite3.Row
db.execute('PRAGMA busy_timeout=10000');db.execute('PRAGMA journal_mode=WAL')
db.execute('''CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,path TEXT,image TEXT,model TEXT,prompt TEXT,
 max_tokens INTEGER,status TEXT,worker TEXT,attempts INTEGER DEFAULT 0,lease REAL DEFAULT 0,
 description TEXT,error TEXT,updated REAL)''')
db.execute('CREATE INDEX IF NOT EXISTS idx_jobs_dispatch ON jobs(status,updated)')
db.commit()
clients={};lock=asyncio.Lock()
async def send(ws,obj): await ws.send(json.dumps(obj,ensure_ascii=False))
def stats():
    counts={r['status']:r['n'] for r in db.execute('SELECT status,count(*) n FROM jobs GROUP BY status')}
    return {'counts':counts,'slaves':[{'name':c['name'],'busy':len(c['assigned']),
       'capacity':c['capacity'],'last_seen':round(time.time()-c['seen'])}
       for c in clients.values() if c['role']=='slave'],
       'masters':sum(c['role']=='master' for c in clients.values())}

async def replay(ws):
    # Reenvío acotado, sin bloquear el event loop con miles de resultados de golpe.
    for r in db.execute("SELECT id,path,description,model FROM jobs WHERE status='done'").fetchall():
        await send(ws,{'type':'result',**dict(r)})

async def schedule():
    async with lock:
        now=time.time()
        db.execute("UPDATE jobs SET status='queued',worker=NULL,updated=? WHERE status='running' AND lease<?",(now,now))
        db.execute("UPDATE jobs SET status='failed',error='Intentos agotados',updated=? WHERE status='queued' AND attempts>=?",(now,a.max_attempts))
        db.commit()
        for ws,c in list(clients.items()):
            if c['role']!='slave' or ws.state.name!='OPEN':continue
            while len(c['assigned'])<c['capacity']:
                job=db.execute("SELECT * FROM jobs WHERE status='queued' AND attempts<? ORDER BY updated LIMIT 1",(a.max_attempts,)).fetchone()
                if not job:break
                db.execute("UPDATE jobs SET status='running',worker=?,attempts=attempts+1,lease=?,updated=? WHERE id=?",
                           (c['name'],now+a.lease,now,job['id']))
                db.commit();c['assigned'].add(job['id'])
                try:
                    await send(ws,{'type':'job','id':job['id'],'image':job['image'],'model':job['model'],
                                   'prompt':job['prompt'],'max_tokens':job['max_tokens']})
                except Exception:
                    c['assigned'].discard(job['id'])
                    db.execute("UPDATE jobs SET status='queued',worker=NULL,updated=? WHERE id=?",(time.time(),job['id']))
                    db.commit();break

async def handler(ws):
    name=None
    try:
        hello=json.loads(await asyncio.wait_for(ws.recv(),10));role=hello.get('role');token=hello.get('token','')
        expected={'master':MASTER,'slave':SLAVE}.get(role)
        if expected is None or not isinstance(token,str) or not hmac.compare_digest(token,expected):
            await ws.close(1008,'Unauthorized');return
        if role=='master' and any(c['role']=='master' for c in clients.values()):
            await ws.close(1008,'Master already connected');return
        name=str(hello.get('name') or role)[:80]
        # No permitir dos slaves con el mismo nombre: la asignación usa ese nombre.
        if role=='slave' and any(c['role']=='slave' and c['name']==name for c in clients.values()):
            await ws.close(1008,'Duplicate slave name');return
        capacity=max(1,min(8,int(hello.get('capacity',1)))) if role=='slave' else 0
        clients[ws]={'role':role,'name':name,'capacity':capacity,'assigned':set(),'seen':time.time()}
        await send(ws,{'type':'registered','role':role})
        print('Conectado',role,name,'capacidad',capacity,flush=True)
        if role=='master':await replay(ws)
        await schedule()
        async for raw in ws:
            m=json.loads(raw);typ=m.get('type');clients[ws]['seen']=time.time()
            if role=='master' and typ=='enqueue':
                jobs=m.get('jobs',[])
                if not isinstance(jobs,list) or len(jobs)>10:continue
                async with lock:
                    inserted=0
                    for j in jobs:
                        if not isinstance(j,dict) or not all(isinstance(j.get(k),str) for k in ('id','path','image','model','prompt')):continue
                        if len(j['image'])>12_000_000:continue
                        cur=db.execute('''INSERT OR IGNORE INTO jobs(id,path,image,model,prompt,max_tokens,status,updated)
                            VALUES(?,?,?,?,?,?,?,?)''',(j['id'],j['path'],j['image'],j['model'],j['prompt'],int(j.get('max_tokens',1600)),'queued',time.time()))
                        inserted+=cur.rowcount
                    db.commit()
                await send(ws,{'type':'enqueued','count':inserted});await schedule()
            elif role=='master' and typ=='replay_results':await replay(ws)
            elif role=='master' and typ=='ack':
                async with lock:
                    db.execute("DELETE FROM jobs WHERE id=? AND status='done'",(m.get('id'),));db.commit()
            elif role=='master' and typ=='stats':await send(ws,{'type':'stats','data':stats()})
            elif role=='slave' and typ=='heartbeat':
                ids=m.get('ids',[])
                if not isinstance(ids,list):ids=[m.get('id')]
                active=set(ids)&clients[ws]['assigned']
                if active:
                    async with lock:
                        db.executemany("UPDATE jobs SET lease=? WHERE id=? AND status='running' AND worker=?",
                                       [(time.time()+a.lease,jid,name) for jid in active]);db.commit()
            elif role=='slave' and typ in ('result','failed'):
                jid=m.get('id');c=clients[ws]
                if jid not in c['assigned']:continue
                async with lock:
                    if typ=='result' and isinstance(m.get('description'),str) and m['description'].strip():
                        db.execute("UPDATE jobs SET status='done',description=?,image=NULL,updated=? WHERE id=? AND status='running' AND worker=?",
                                   (m['description'].strip(),time.time(),jid,name))
                    else:
                        db.execute("UPDATE jobs SET status=CASE WHEN attempts>=? THEN 'failed' ELSE 'queued' END,worker=NULL,error=?,updated=? WHERE id=? AND worker=?",
                                   (a.max_attempts,str(m.get('error','Respuesta vacía'))[:500],time.time(),jid,name))
                    db.commit();c['assigned'].discard(jid)
                    result=db.execute("SELECT id,path,description,model FROM jobs WHERE id=? AND status='done'",(jid,)).fetchone()
                if result:
                    for mw,mc in list(clients.items()):
                        if mc['role']=='master':
                            try:await send(mw,{'type':'result',**dict(result)})
                            except Exception:pass
                await schedule()
    except (websockets.exceptions.ConnectionClosed,asyncio.TimeoutError,ValueError,TypeError) as exc:
        print('Desconectado',name,str(exc)[:120],flush=True)
    finally:
        c=clients.pop(ws,None)
        if c and c['assigned']:
            async with lock:
                db.executemany("UPDATE jobs SET status='queued',worker=NULL,updated=? WHERE id=? AND status='running' AND worker=?",
                               [(time.time(),jid,c['name']) for jid in c['assigned']]);db.commit()
        await schedule()

HTML='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>jocarsa | fotos</title><style>body{font:16px system-ui;background:#eee;color:#333;margin:40px}main{max-width:1100px;margin:auto}.cards{display:flex;gap:12px;flex-wrap:wrap}.card{background:white;border-radius:14px;padding:24px;min-width:130px;box-shadow:0 2px 8px #0001}strong{font-size:30px}table{width:100%;border-collapse:collapse;background:white}td,th{padding:14px;text-align:left;border-bottom:1px solid #ddd}</style><main><h1>jocarsa | fotos</h1><p>Monitor distribuido</p><div id="cards" class="cards"></div><h2>Trabajadores</h2><table><thead><tr><th>Equipo</th><th>Ocupación</th><th>Última actividad</th></tr></thead><tbody id="workers"></tbody></table><p id="error"></p></main><script>let token=sessionStorage.getItem('monitor_token')||prompt('Token de monitor');if(token)sessionStorage.setItem('monitor_token',token);async function refresh(){try{let r=await fetch('/api',{headers:{Authorization:'Bearer '+token}});if(!r.ok)throw Error('Autenticación fallida');let s=await r.json();document.getElementById('cards').replaceChildren(...['queued','running','done','failed'].map(k=>{let d=document.createElement('div');d.className='card';let n=document.createElement('strong');n.textContent=s.counts[k]||0;let p=document.createElement('p');p.textContent=k;d.append(n,p);return d}));let t=document.getElementById('workers');t.replaceChildren(...s.slaves.map(w=>{let tr=document.createElement('tr');[w.name,w.busy+'/'+w.capacity,w.last_seen+' s'].forEach(v=>{let td=document.createElement('td');td.textContent=v;tr.append(td)});return tr}));document.getElementById('error').textContent='Masters conectados: '+s.masters}catch(e){document.getElementById('error').textContent=e.message}}refresh();setInterval(refresh,1000)</script></html>'''
async def monitor(reader,writer):
    try:
        request=await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'),5)
        lines=request.decode('latin1').split('\r\n');path=lines[0].split(' ')[1]
        headers={x.split(':',1)[0].lower():x.split(':',1)[1].strip() for x in lines[1:] if ':' in x}
        if path.startswith('/api') and not hmac.compare_digest(headers.get('authorization',''),'Bearer '+MONITOR):
            body=b'Unauthorized';code='401 Unauthorized';ct='text/plain'
        elif path.startswith('/api'):
            body=json.dumps(stats()).encode();code='200 OK';ct='application/json'
        else:body=HTML.encode();code='200 OK';ct='text/html; charset=utf-8'
        writer.write(f'HTTP/1.1 {code}\r\nContent-Type: {ct}\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n'.encode()+body)
        await writer.drain()
    except Exception:pass
    finally:
        writer.close()
        try:await writer.wait_closed()
        except Exception:pass
async def ticker():
    while True:
        await asyncio.sleep(5);await schedule()
async def main():
    async with websockets.serve(handler,a.host,a.port,max_size=64*1024*1024,ping_interval=20,ping_timeout=40),await asyncio.start_server(monitor,a.host,a.monitor_port):
        print('WebSocket',a.port,'Monitor',a.monitor_port,flush=True)
        await ticker()
if __name__=='__main__':asyncio.run(main())
