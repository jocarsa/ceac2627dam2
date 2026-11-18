#!/usr/bin/env python3
"""Esclavo Ollama: precarga en RAM, sin guardar fotografías en disco."""
import argparse,asyncio,json,socket
from urllib.request import Request,urlopen
import websockets
TOKEN='y3sSimNlzDr7UNEZ6gYXlwsP-na5lrCeUwyffKQ4C0sirfwv'
p=argparse.ArgumentParser()
p.add_argument('--server',default='ws://jocarsa.com:8765')
p.add_argument('--ollama',default='http://127.0.0.1:11434')
p.add_argument('--name',default=socket.gethostname())
p.add_argument('--timeout',type=int,default=1200)
p.add_argument('--prefetch',type=int,default=2)
a=p.parse_args()
def infer(job):
    body=json.dumps({'model':job['model'],'messages':[{'role':'user','content':job['prompt'],
        'images':[job['image']]}],'stream':False,'options':{'temperature':0.2,'num_predict':job['max_tokens']}}).encode()
    req=Request(a.ollama.rstrip('/')+'/api/chat',data=body,headers={'Content-Type':'application/json'})
    with urlopen(req,timeout=a.timeout) as resp:data=json.load(resp)
    answer=data.get('message',{}).get('content','').strip()
    if not answer:raise ValueError('Respuesta vacía de Ollama')
    return answer
async def run():
    while True:
        try:
            async with websockets.connect(a.server,max_size=32*1024*1024,ping_interval=20,ping_timeout=40) as ws:
                await ws.send(json.dumps({'role':'slave','token':TOKEN,'name':a.name,'capacity':max(1,min(8,a.prefetch))}))
                response=json.loads(await ws.recv())
                if response.get('type')!='registered':raise RuntimeError('Registro rechazado')
                print('Conectado:',a.name,'precarga',a.prefetch,flush=True)
                queue=asyncio.Queue(maxsize=max(1,min(8,a.prefetch)))
                active=set()
                async def heartbeat():
                    while True:
                        await asyncio.sleep(20)
                        if active:await ws.send(json.dumps({'type':'heartbeat','ids':list(active)}))
                async def process():
                    while True:
                        job=await queue.get();jid=job['id']
                        print('Procesando',jid[:12],flush=True)
                        try:
                            result=await asyncio.to_thread(infer,job)
                            await ws.send(json.dumps({'type':'result','id':jid,'description':result},ensure_ascii=False))
                            print('Completado',jid[:12],flush=True)
                        except Exception as exc:
                            await ws.send(json.dumps({'type':'failed','id':jid,'error':str(exc)}))
                            print('Error',jid[:12],exc,flush=True)
                        finally:
                            active.discard(jid);job.clear();queue.task_done()
                worker=asyncio.create_task(process());hb=asyncio.create_task(heartbeat())
                try:
                    async for raw in ws:
                        job=json.loads(raw)
                        if job.get('type')!='job':continue
                        active.add(job['id']);await queue.put(job)
                finally:
                    worker.cancel();hb.cancel()
                    await asyncio.gather(worker,hb,return_exceptions=True)
                    while not queue.empty():
                        j=queue.get_nowait();j.clear();queue.task_done()
                    active.clear()
        except (OSError,websockets.exceptions.ConnectionClosed,RuntimeError) as exc:
            print('Reconectando en 5 s:',exc,flush=True);await asyncio.sleep(5)
if __name__=='__main__':asyncio.run(run())
