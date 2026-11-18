#!/usr/bin/env python3
"""Trabajador Ollama remoto: pip install websockets"""
import argparse,asyncio,json,os,socket,time
from urllib.request import Request,urlopen
import websockets
P=argparse.ArgumentParser();P.add_argument('--server',default='ws://jocarsa.com:8765');P.add_argument('--ollama',default='http://127.0.0.1:11434');P.add_argument('--name',default=socket.gethostname());P.add_argument('--timeout',type=int,default=1200);A=P.parse_args()
TOKEN='y3sSimNlzDr7UNEZ6gYXlwsP-na5lrCeUwyffKQ4C0sirfwv'
def infer(job):
    body=json.dumps({'model':job['model'],'messages':[{'role':'user','content':job['prompt'],'images':[job['image']]}],'stream':False,'options':{'temperature':0.2,'num_predict':job['max_tokens']}}).encode()
    req=Request(A.ollama.rstrip('/')+'/api/chat',data=body,headers={'Content-Type':'application/json'})
    with urlopen(req,timeout=A.timeout) as response: data=json.load(response)
    answer=data.get('message',{}).get('content','').strip()
    if not answer:raise ValueError('Respuesta vacia de Ollama')
    return answer
async def main():
    while True:
        try:
            async with websockets.connect(A.server,max_size=16*1024*1024,ping_interval=20,ping_timeout=30) as ws:
                await ws.send(json.dumps({'role':'slave','token':TOKEN,'name':A.name}));print('Registrado:',await ws.recv(),flush=True)
                async for raw in ws:
                    job=json.loads(raw)
                    if job.get('type')!='job':continue
                    jid=job['id'];print('Procesando',jid[:12],flush=True)
                    async def heartbeat():
                        while True:
                            await asyncio.sleep(20);await ws.send(json.dumps({'type':'heartbeat','id':jid}))
                    hb=asyncio.create_task(heartbeat())
                    try:
                        answer=await asyncio.to_thread(infer,job)
                        await ws.send(json.dumps({'type':'result','id':jid,'description':answer},ensure_ascii=False));print('Completado',jid[:12],flush=True)
                    except Exception as e:
                        await ws.send(json.dumps({'type':'failed','id':jid,'error':str(e)}));print('Error:',e,flush=True)
                    finally:
                        hb.cancel()
                        # La imagen se utiliza solo en memoria: no se escribe a disco.
                        job.clear()
        except (OSError,websockets.exceptions.ConnectionClosed) as e:
            print('Desconectado:',e,flush=True);await asyncio.sleep(5)
asyncio.run(main())