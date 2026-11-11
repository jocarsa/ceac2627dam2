# Jocarsa | Aventureros multijugador con chat

## Ejecutar

```bash
pip install websockets
python3 servidor.py
```

En otra terminal:

```bash
python3 -m http.server 8000
```

Abre http://localhost:8000 y pulsa Conectar. Para probar multijugador, abre dos pestañas.

## Controles

- WASD / flechas: mover personaje
- Chat: escribir en el panel lateral y pulsar Enter o Enviar
- Los mensajes aparecen como bocadillos durante cinco segundos encima de los personajes
- En la lista lateral se muestran nombres y coordenadas X/Y

Si accedes desde otro dispositivo, usa la IP del servidor en el navegador. Abre los puertos 8000 y 8765 en el firewall si es necesario. Para HTTPS usa un proxy con WebSockets seguros (wss).
