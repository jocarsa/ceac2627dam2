
from flask import Flask, render_template_string, request, jsonify
import socket
import threading
import queue

app = Flask(__name__)

IP = "10.4.193.182"
PUERTO = 5000

conexion = None
mensajes = queue.Queue()
lock = threading.Lock()


def recibir():
    global conexion

    buffer = b""

    try:
        while True:
            datos = conexion.recv(4096)

            if not datos:
                break

            buffer += datos

            while b"\n" in buffer:
                linea, buffer = buffer.split(b"\n", 1)
                mensajes.put(linea.decode("utf-8", errors="replace"))

    except OSError:
        pass

    mensajes.put("Desconectado del servidor")


def conectar():
    global conexion

    try:
        conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexion.connect((IP, PUERTO))

        threading.Thread(target=recibir, daemon=True).start()

        print("Conectado al servidor")

    except OSError as error:
        print("Error de conexión:", error)
        conexion = None


HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chat TCP</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #edf1f5;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.chat {
    width: 650px;
    max-width: 95vw;
    height: 80vh;
    background: white;
    border-radius: 14px;
    box-shadow: 0 10px 35px #0002;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

header {
    padding: 22px;
    background: #25364a;
    color: white;
}

header h2 {
    margin: 0 0 6px;
}

header small {
    opacity: .7;
}

#mensajes {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.mensaje {
    padding: 12px 16px;
    border-radius: 12px;
    max-width: 80%;
    overflow-wrap: anywhere;
    background: #edf1f5;
    align-self: flex-start;
}

.propio {
    background: #d5e8ff;
    align-self: flex-end;
}

.sistema {
    background: #fff1d6;
    color: #795500;
    align-self: center;
    font-size: 13px;
}

footer {
    padding: 16px;
    border-top: 1px solid #ddd;
    display: flex;
    gap: 10px;
}

input {
    flex: 1;
    padding: 13px;
    border: 1px solid #ddd;
    border-radius: 8px;
    outline: none;
    min-width: 0;
}

button {
    padding: 12px 22px;
    background: #25364a;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}

button:hover {
    background: #385475;
}
</style>
</head>

<body>

<div class="chat">

    <header>
        <h2>Chat TCP</h2>
        <small>Servidor: 10.4.193.182:5000</small>
    </header>

    <div id="mensajes"></div>

    <footer>
        <input
            id="mensaje"
            placeholder="Escribe un mensaje..."
            maxlength="200"
            autocomplete="off"
        >
        <button onclick="enviar()">Enviar</button>
    </footer>

</div>

<script>
const caja = document.getElementById("mensajes");
const entrada = document.getElementById("mensaje");

function agregar(texto, tipo = "") {
    const elemento = document.createElement("div");
    elemento.className = "mensaje " + tipo;
    elemento.textContent = texto;

    caja.appendChild(elemento);
    caja.scrollTop = caja.scrollHeight;
}

async function enviar() {
    const texto = entrada.value.trim();

    if (!texto) return;

    try {
        const respuesta = await fetch("/enviar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({mensaje: texto})
        });

        const datos = await respuesta.json();

        if (datos.ok) {
            agregar(texto, "propio");
            entrada.value = "";
        } else {
            agregar(datos.error, "sistema");
        }
    } catch (error) {
        agregar("Error enviando mensaje", "sistema");
    }
}

entrada.addEventListener("keydown", function(evento) {
    if (evento.key === "Enter") {
        enviar();
    }
});

async function recibir() {
    try {
        const respuesta = await fetch("/recibir");
        const datos = await respuesta.json();

        for (const mensaje of datos.mensajes) {
            agregar(mensaje);
        }
    } catch (error) {
        console.error(error);
    }
}

setInterval(recibir, 500);
recibir();
</script>

</body>
</html>
"""


@app.route("/")
def inicio():
    return render_template_string(HTML)


@app.route("/enviar", methods=["POST"])
def enviar():
    datos = request.get_json(silent=True) or {}
    mensaje = datos.get("mensaje", "")

    if not isinstance(mensaje, str):
        return jsonify(ok=False, error="Mensaje inválido")

    if not mensaje.strip():
        return jsonify(ok=False, error="Mensaje vacío")

    if len(mensaje) > 200:
        return jsonify(ok=False, error="Máximo 200 caracteres")

    if "\n" in mensaje or "\r" in mensaje:
        return jsonify(ok=False, error="No se permiten saltos de línea")

    if conexion is None:
        return jsonify(ok=False, error="Sin conexión al servidor")

    try:
        with lock:
            conexion.sendall((mensaje + "\n").encode("utf-8"))

        return jsonify(ok=True)

    except OSError:
        return jsonify(ok=False, error="Error de conexión")


@app.route("/recibir")
def obtener_mensajes():
    resultado = []

    while not mensajes.empty():
        try:
            resultado.append(mensajes.get_nowait())
        except queue.Empty:
            break

    return jsonify(mensajes=resultado)


if __name__ == "__main__":
    conectar()
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False,
        threaded=True
    )
