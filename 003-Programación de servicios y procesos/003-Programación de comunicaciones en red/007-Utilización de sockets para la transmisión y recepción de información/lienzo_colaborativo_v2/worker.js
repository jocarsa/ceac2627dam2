'use strict';
// Procesa y valida mensajes de red fuera del hilo principal.
let socket=null,host='',reconnect=null,loginName='';
function post(kind,data={}){self.postMessage({kind,...data})}
function connect(){
  socket=new WebSocket(host);
  socket.onopen=()=>{post('status',{connected:true});socket.send(JSON.stringify({type:'login',name:loginName}))};
  socket.onclose=()=>{post('status',{connected:false});reconnect=setTimeout(connect,1800)};
  socket.onerror=()=>socket.close();
  socket.onmessage=e=>{
    try{
      const m=JSON.parse(e.data);
      if(!m||typeof m.type!=='string')return;
      // Preparación de mensajes y coordenadas en worker.
      if(m.type==='point' && (!Array.isArray(m.point)||m.point.length!==2))return;
      post('message',{message:m});
    }catch{}
  };
}
self.onmessage=e=>{
  const m=e.data;
  if(m.kind==='connect'){loginName=m.name;host=m.url;clearTimeout(reconnect);if(socket)socket.close();connect()}
  if(m.kind==='send' && socket?.readyState===WebSocket.OPEN)socket.send(JSON.stringify(m.message));
};
