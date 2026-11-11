# Lienzo colaborativo v2

Instala: pip install -r requirements.txt
Servidor WebSocket: python3 servidor.py
Servidor web (otra terminal): python3 -m http.server 8000
Navegador: http://localhost:8000

Incluye Web Worker para WebSocket y análisis de mensajes; el Canvas se dibuja en hilo principal para conservar compatibilidad. Python asyncio maneja muchas conexiones sin necesidad de multicore. SQLite usa WAL y operaciones en hilos para evitar bloquear el event loop. Para escalar a varios procesos se necesitaría un broker compartido (Redis Pub/Sub) y afinidad/estado coordinado; lanzar múltiples workers sin ello rompería la sincronización.

Login: solo nombre visible, no autenticación segura ni contraseñas. Cada sesión tiene un identificador efímero. Deshacer se limita a trazos de la sesión actual. En producción usar HTTPS/WSS, autenticación real, permisos y limitación de tráfico.
