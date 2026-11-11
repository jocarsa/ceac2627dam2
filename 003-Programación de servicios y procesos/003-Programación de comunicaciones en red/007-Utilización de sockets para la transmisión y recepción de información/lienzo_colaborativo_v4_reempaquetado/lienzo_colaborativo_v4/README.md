# jocarsa | vida colaborativa v4

Lienzo de 1920 × 1080 píxeles, dividido en 192 × 108 celdas de 10 píxeles. Juego de la Vida de Conway calculado exclusivamente por el servidor. Los usuarios pueden pintar y borrar células en tiempo real mientras la simulación sigue ejecutándose. El color identifica el cursor, no el estado de las células.

## Iniciar

```bash
pip install -r requirements.txt
python3 servidor.py
```

En otra terminal:

```bash
python3 -m http.server 8000
```

Abrir http://localhost:8000 o http://IP_DEL_SERVIDOR:8000. Si se sirve con Apache en el puerto 80, abrir http://10.4.193.182/ (colocar index.html y worker.js en el DocumentRoot).

## Administrador

La autorización se realiza con la IP de **origen del socket**, no con la URL de destino. Por defecto 10.4.193.182, 127.0.0.1 y ::1 son administradores. Se configura con ADMIN_IPS. Si un proxy termina el WebSocket, el servidor verá la IP del proxy; no confiar en X-Forwarded-For sin un proxy controlado. La identificación es solo por nombre, sin contraseña: los baneos por nombre se pueden evadir cambiando el nombre. Para producción usar autenticación real.

Los administradores pueden pausar, reanudar, avanzar una generación, limpiar y banear/desbanear nombres. Baneos y estado del mundo se guardan en SQLite (`vida.sqlite3`). El mundo se guarda periódicamente cada 20 generaciones y en cierre normal.

## Rendimiento

Un Web Worker mantiene el WebSocket fuera del hilo principal. El servidor usa asyncio, y la simulación usa un conjunto disperso de células; un único proceso mantiene el estado coherente. Los mensajes de estado contienen todas las células vivas, lo que es apropiado para pruebas de aula pero puede saturar la red si el tablero está muy poblado. Para escalar, transmitir diferencias y usar buffers binarios. Se puede ajustar TICK_SECONDS (por defecto 0.25) y CELL_SIZE (por defecto 10, divisor exacto de 1920 y 1080).
