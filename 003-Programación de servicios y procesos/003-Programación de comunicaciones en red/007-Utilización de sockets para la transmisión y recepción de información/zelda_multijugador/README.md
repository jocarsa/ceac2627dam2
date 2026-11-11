# Aventureros del bosque

## Instalar

```bash
python3 -m pip install websockets
```

## Ejecutar

Terminal 1:
```bash
python3 servidor.py
```

Terminal 2:
```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

Abrir `http://localhost:8000` en varios navegadores. En red local, sustituir localhost por la IP del servidor. Abrir puertos 8000 y 8765 si corresponde.

**Nota:** el cliente conecta a WebSocket en el mismo hostname, puerto 8765. Para HTTPS en producción, configurar un proxy inverso WSS (puerto/ruta) y adaptar la URL de conexión.

**Limitaciones de esta demo:** movimiento validado por obstáculos pero sin control de velocidad por cliente; no es un servidor antitrampas. No hay persistencia, combate ni salas.
