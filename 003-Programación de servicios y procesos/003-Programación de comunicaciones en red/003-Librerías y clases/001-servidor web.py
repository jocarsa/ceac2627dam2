from http.server import HTTPServer, BaseHTTPRequestHandler

class Servidor(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>Hola desde Python</h1>")

servidor = HTTPServer(("localhost", 8000), Servidor)
print("Servidor en http://localhost:8000")
servidor.serve_forever()
