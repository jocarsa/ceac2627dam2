from http.server import HTTPServer, SimpleHTTPRequestHandler

servidor = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)

print("Servidor iniciado en http://localhost:8000")

servidor.serve_forever()