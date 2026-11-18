#!/usr/bin/env python3
"""Master: un único escaneo por ejecución, preparación paralela y ventana acotada."""
import argparse, asyncio, hashlib, json, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import websockets
from describir_fotos_original import EXTENSIONES, PROMPT, preparar_imagen, conectar

TOKEN='yhVHs0O8ZEZZkR_stCNGjY7OG-THoJsadab18oounmXV64Bn'
p=argparse.ArgumentParser()
p.add_argument('--destino',type=Path,default=Path('destino'))
p.add_argument('--bd',type=Path,default=Path('fotografias.sqlite3'))
p.add_argument('--server',default='ws://jocarsa.com:8765')
p.add_argument('--modelo',default='gemma3:4b')
p.add_argument('--max-lado',type=int,default=1536)
p.add_argument('--calidad',type=int,default=80)
p.add_argument('--max-tokens',type=int,default=1600)
p.add_argument('--ventana',type=int,default=100)
p.add_argument('--hilos',type=int,default=4)
p.add_argument('--lote',type=int,default=5)
a=p.parse_args()
root=a.destino.resolve()
if not root.is_dir(): raise SystemExit('No existe '+str(root))
a.bd.parent.mkdir(parents=True,exist_ok=True)
db=conectar(a.bd)

# Nunca repetir el escaneo durante esta ejecución, incluso después de reconectar.
def scan_once():
    print('Escaneo único inicial...',flush=True)
    known={r[0]:(r[1],r[2],r[3]) for r in db.execute('SELECT ruta,tamano_bytes,fecha_modificacion_ns,modelo FROM fotografias')}
    todo={}; total=0
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONES or path.name.startswith('._'): continue
        try:
            st=path.stat(); key=str(path); total+=1
            if known.get(key)==(st.st_size,st.st_mtime_ns,a.modelo): continue
            jid=hashlib.sha256(f'{key}|{st.st_size}|{st.st_mtime_ns}|{a.modelo}'.encode()).hexdigest()
            todo[jid]=(path,st.st_size,st.st_mtime_ns)
        except OSError: continue
    print(f'Escaneo terminado. Total: {total} | Pendientes: {len(todo)}',flush=True)
    return todo

async def main():
    todo=scan_once()
    if not todo: return
    # El diccionario solo contiene rutas/metadatos, nunca imágenes.
    ids=list(todo)
    next_index=0
    done=set()
    in_flight=set()
    failed_preparation=set()
    pool=ThreadPoolExecutor(max_workers=max(1,a.hilos))
    loop=asyncio.get_running_loop()
    write_lock=asyncio.Lock()
    async def save_result(m,ws):
        jid=m.get('id')
        if jid not in todo:
            await ws.send(json.dumps({'type':'ack','id':jid}));return
        path,size,mtime=todo[jid]
        try:
            st=path.stat()
            if (st.st_size,st.st_mtime_ns)!=(size,mtime):
                print('Fotografía modificada durante el proceso:',path,flush=True)
                # No guardar un resultado que ya no corresponde al archivo.
            else:
                async with write_lock:
                    db.execute('''INSERT INTO fotografias(ruta,descripcion,modelo,tamano_bytes,fecha_modificacion_ns,fecha_analisis)
                        VALUES(?,?,?,?,?,?) ON CONFLICT(ruta) DO UPDATE SET
                        descripcion=excluded.descripcion,modelo=excluded.modelo,tamano_bytes=excluded.tamano_bytes,
                        fecha_modificacion_ns=excluded.fecha_modificacion_ns,fecha_analisis=excluded.fecha_analisis''',
                        (str(path),m['description'],m['model'],size,mtime,datetime.now().isoformat(timespec='seconds')))
                    db.commit()
        except OSError:
            print('Archivo desaparecido:',path,flush=True)
        done.add(jid);in_flight.discard(jid)
        await ws.send(json.dumps({'type':'ack','id':jid}))
        if len(done)%10==0 or len(done)==len(todo):
            print(f'Completadas: {len(done)}/{len(todo)} | En tránsito: {len(in_flight)}',flush=True)

    try:
        while len(done)+len(failed_preparation)<len(todo):
            try:
                async with websockets.connect(a.server,max_size=32*1024*1024,ping_interval=20,ping_timeout=40) as ws:
                    await ws.send(json.dumps({'role':'master','token':TOKEN}))
                    if json.loads(await ws.recv()).get('type')!='registered':raise RuntimeError('Registro rechazado')
                    print('Master conectado',flush=True)
                    # El servidor reenvía los resultados persistidos tras cada reconexión.
                    in_flight.clear();next_index=0
                    # El receptor no espera a la preparación de imágenes.
                    async def receiver():
                        async for raw in ws:
                            m=json.loads(raw)
                            if m.get('type')=='result': await save_result(m,ws)
                            elif m.get('type')=='failed':
                                print('Trabajo fallido en servidor:',m.get('id'),m.get('error'),flush=True)
                    recv_task=asyncio.create_task(receiver())
                    try:
                        while not recv_task.done() and len(done)+len(failed_preparation)<len(todo):
                            capacity=max(0,a.ventana-len(in_flight))
                            batch_ids=[]
                            while next_index<len(ids) and len(batch_ids)<min(a.lote,capacity):
                                jid=ids[next_index];next_index+=1
                                if jid not in done and jid not in failed_preparation and jid not in in_flight:
                                    batch_ids.append(jid);in_flight.add(jid)
                            if batch_ids:
                                async def prepare(jid):
                                    path,_,_=todo[jid]
                                    try:
                                        img=await loop.run_in_executor(pool,preparar_imagen,path,a.max_lado,a.calidad)
                                        return {'id':jid,'path':str(path),'image':img,'model':a.modelo,'prompt':PROMPT,'max_tokens':a.max_tokens}
                                    except Exception as exc:
                                        print('Error preparando',path,exc,flush=True)
                                        failed_preparation.add(jid);in_flight.discard(jid)
                                        return None
                                prepared=await asyncio.gather(*(prepare(j) for j in batch_ids))
                                jobs=[x for x in prepared if x]
                                if jobs:
                                    await ws.send(json.dumps({'type':'enqueue','jobs':jobs},ensure_ascii=False))
                                continue
                            # Sin escaneo, solo espera resultados o reconexión.
                            await asyncio.sleep(.2 if in_flight else 1)
                            if not in_flight and next_index>=len(ids) and len(done)+len(failed_preparation)<len(todo):
                                # Puede haber resultados persistidos en el broker; consultar estado.
                                await ws.send(json.dumps({'type':'replay_results'}))
                                await asyncio.sleep(2)
                        if recv_task.done(): await recv_task
                    finally:
                        recv_task.cancel()
                        try: await recv_task
                        except asyncio.CancelledError: pass
            except (OSError,websockets.exceptions.ConnectionClosed,RuntimeError) as exc:
                print('Reconexión en 5 s:',exc,flush=True)
                await asyncio.sleep(5)
        print(f'FINALIZADO: {len(done)} completadas; {len(failed_preparation)} errores de preparación.',flush=True)
    finally:
        pool.shutdown(wait=False,cancel_futures=True)
        db.close()

if __name__=='__main__': asyncio.run(main())
