import json
import secrets
import socket
import threading
from collections import deque
from flask import Flask, render_template_string, request, jsonify, session

IP = "10.4.193.182"
PUERTO = 5000
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
conexiones = {}
conexiones_lock = threading.RLock()


class ClienteTCP:
    def __init__(self, nombre):
        self.nombre = nombre
        self.sock = socket.create_connection((IP, PUERTO), timeout=5)
        self.sock.settimeout(None)
        self.lock = threading.Lock()
        self.eventos = deque(maxlen=300)
        self.numero = 0
        self.activo = True
        self.enviar_paquete({"tipo": "identificar", "nombre": nombre})
        self.hilo = threading.Thread(target=self.recibir, daemon=True)
        self.hilo.start()

    def enviar_paquete(self, paquete):
        datos = (json.dumps(paquete, ensure_ascii=False) + "\n").encode("utf-8")
        with self.lock:
            self.sock.sendall(datos)

    def recibir(self):
        buffer = b""
        try:
            while self.activo:
                datos = self.sock.recv(4096)
                if not datos:
                    break
                buffer += datos
                if len(buffer) > 65536:
                    break
                while b"\n" in buffer:
                    linea, buffer = buffer.split(b"\n", 1)
                    try:
                        paquete = json.loads(linea.decode("utf-8"))
                    except (ValueError, UnicodeDecodeError):
                        continue
                    with self.lock:
                        self.numero += 1
                        paquete["id"] = self.numero
                        self.eventos.append(paquete)
        except OSError:
            pass
        finally:
            self.activo = False
            with self.lock:
                self.numero += 1
                self.eventos.append({"id": self.numero, "tipo": "sistema", "texto": "Conexión cerrada"})
            try:
                self.sock.close()
            except OSError:
                pass

    def cerrar(self):
        self.activo = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()


HTML = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chat TCP · Identificación</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#eef2f7;font-family:system-ui,Arial,sans-serif;color:#243246;min-height:100vh;display:grid;place-items:center}
.chat{width:min(760px,96vw);height:min(780px,94vh);background:white;border-radius:16px;box-shadow:0 14px 50px #152a4520;display:flex;flex-direction:column;overflow:hidden}
header{background:#25364a;color:white;padding:18px 22px;display:flex;justify-content:space-between;align-items:center;gap:12px}header h2{margin:0;font-size:21px}header small{opacity:.7}header button{background:#ffffff20;border:1px solid #ffffff40;color:white}
#mensajes{flex:1;overflow-y:auto;padding:22px;display:flex;flex-direction:column;gap:12px}.burbuja{max-width:82%;padding:11px 15px;border-radius:13px;background:#edf1f5;overflow-wrap:anywhere;align-self:flex-start}.burbuja.propio{background:#d5e8ff;align-self:flex-end}.burbuja.sistema,.burbuja.error{align-self:center;background:#fff1d6;color:#795500;font-size:13px}.burbuja.error{background:#ffe0e0;color:#9b2020}.nombre{font-size:12px;font-weight:700;margin-bottom:5px;opacity:.75}
footer{display:flex;gap:10px;padding:16px;border-top:1px solid #e5e8ed}input{flex:1;min-width:0;padding:13px;border:1px solid #d5dbe3;border-radius:9px;font:inherit}button{padding:11px 18px;background:#25364a;color:white;border:0;border-radius:9px;cursor:pointer;font:inherit}button:hover{filter:brightness(1.15)}
#login{position:fixed;inset:0;background:#eef2f7;display:grid;place-items:center;z-index:10}#login.oculto{display:none}.panel{background:white;padding:32px;border-radius:16px;box-shadow:0 12px 40px #152a4520;width:min(390px,92vw);display:grid;gap:14px}.panel h2{margin:0}.panel p{margin:0;color:#667;font-size:14px}.panel button{width:100%}#estado{font-size:13px;color:#b92c2c;min-height:18px}
</style>
</head>
<body>
<div id="login"><form class="panel" id="formLogin"><h2>Identifícate</h2><p>Introduce un nombre único para participar en el chat.</p><input id="nombre" maxlength="24" placeholder="Tu nombre" required autocomplete="nickname"><button>Entrar al chat</button><div id="estado"></div></form></div>
<div class="chat"><header><div><h2>Chat TCP</h2><small id="usuarioActual">Sin identificar</small></div><button id="salir">Salir</button></header><main id="mensajes"></main><footer><input id="mensaje" maxlength="200" placeholder="Escribe un mensaje..." autocomplete="off"><button id="enviar">Enviar</button></footer></div>
<script>
let usuario='', ultimo=0;
const mensajes=document.getElementById('mensajes');
function agregar(p){
  const el=document.createElement('div');
  const propio=p.tipo==='mensaje' && p.usuario===usuario;
  el.className='burbuja '+(propio?'propio':p.tipo==='sistema'?'sistema':p.tipo==='error'?'error':'');
  if(p.tipo==='mensaje'){
    const nombre=document.createElement('div');nombre.className='nombre';nombre.textContent=p.usuario||'Desconocido';el.appendChild(nombre);
  }
  const texto=document.createElement('div');texto.textContent=p.texto||'';el.appendChild(texto);
  mensajes.appendChild(el);mensajes.scrollTop=mensajes.scrollHeight;
}
async function entrar(nombre){
  const r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre})});
  const d=await r.json();if(!d.ok)throw Error(d.error||'No se pudo conectar');
  usuario=d.nombre;ultimo=0;mensajes.replaceChildren();document.getElementById('usuarioActual').textContent='Conectado como '+usuario;
  document.getElementById('login').classList.add('oculto');
}
document.getElementById('formLogin').onsubmit=async e=>{
  e.preventDefault();const estado=document.getElementById('estado');estado.textContent='Conectando...';
  try{await entrar(document.getElementById('nombre').value.trim());estado.textContent='';}catch(error){estado.textContent=error.message;}
};
async function enviar(){
  const campo=document.getElementById('mensaje');const texto=campo.value.trim();if(!texto||!usuario)return;
  try{
    const r=await fetch('/enviar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({texto})});
    const d=await r.json();if(!d.ok)throw Error(d.error);
    campo.value='';
  }catch(error){agregar({tipo:'error',texto:error.message});}
}
document.getElementById('enviar').onclick=enviar;
document.getElementById('mensaje').onkeydown=e=>{if(e.key==='Enter')enviar()};
document.getElementById('salir').onclick=async()=>{await fetch('/logout',{method:'POST'});location.reload()};
async function actualizar(){
  if(!usuario)return;
  try{
    const r=await fetch('/recibir?desde='+ultimo);
    if(r.status===401){location.reload();return;}
    const d=await r.json();
    for(const p of d.mensajes){ultimo=Math.max(ultimo,p.id);if(p.tipo==='identificado')continue;agregar(p);}
  }catch(e){console.error(e)}
}
setInterval(actualizar,500);
</script>
</body>
</html>'''


def obtener_cliente():
    identificador = session.get("chat_id")
    with conexiones_lock:
        return conexiones.get(identificador)


@app.route("/")
def inicio():
    return render_template_string(HTML)


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("nombre", "")
    if not isinstance(nombre, str):
        return jsonify(ok=False, error="Nombre inválido"), 400
    nombre = nombre.strip()
    if not (1 <= len(nombre) <= 24) or any(ord(c) < 32 for c in nombre):
        return jsonify(ok=False, error="El nombre debe tener entre 1 y 24 caracteres"), 400
    anterior = obtener_cliente()
    if anterior:
        anterior.cerrar()
        with conexiones_lock:
            conexiones.pop(session.get("chat_id"), None)
    try:
        cliente = ClienteTCP(nombre)
    except OSError as error:
        return jsonify(ok=False, error=f"No se puede conectar al servidor: {error}"), 503
    # Esperar confirmación del servidor antes de aceptar la identificación.
    import time
    limite = time.monotonic() + 5
    while time.monotonic() < limite:
        with cliente.lock:
            eventos = list(cliente.eventos)
        if any(e.get("tipo") == "identificado" for e in eventos):
            identificador = secrets.token_urlsafe(32)
            session["chat_id"] = identificador
            with conexiones_lock:
                conexiones[identificador] = cliente
            return jsonify(ok=True, nombre=nombre)
        error = next((e.get("texto") for e in eventos if e.get("tipo") == "error"), None)
        if error or not cliente.activo:
            cliente.cerrar()
            return jsonify(ok=False, error=error or "Conexión rechazada"), 409
        time.sleep(.05)
    cliente.cerrar()
    return jsonify(ok=False, error="Tiempo de identificación agotado"), 504


@app.route("/enviar", methods=["POST"])
def enviar():
    cliente = obtener_cliente()
    if not cliente or not cliente.activo:
        return jsonify(ok=False, error="No estás conectado"), 401
    datos = request.get_json(silent=True) or {}
    texto = datos.get("texto", "")
    if not isinstance(texto, str) or not texto.strip() or len(texto) > 200 or "\n" in texto or "\r" in texto:
        return jsonify(ok=False, error="Mensaje inválido (máximo 200 caracteres)"), 400
    try:
        cliente.enviar_paquete({"tipo": "mensaje", "texto": texto})
        return jsonify(ok=True)
    except OSError:
        return jsonify(ok=False, error="Conexión perdida"), 503


@app.route("/recibir")
def recibir():
    cliente = obtener_cliente()
    if not cliente:
        return jsonify(ok=False, mensajes=[]), 401
    try:
        desde = max(0, int(request.args.get("desde", 0)))
    except ValueError:
        desde = 0
    with cliente.lock:
        nuevos = [e.copy() for e in cliente.eventos if e["id"] > desde]
    return jsonify(ok=True, mensajes=nuevos)


@app.route("/logout", methods=["POST"])
def logout():
    identificador = session.pop("chat_id", None)
    with conexiones_lock:
        cliente = conexiones.pop(identificador, None)
    if cliente:
        cliente.cerrar()
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
