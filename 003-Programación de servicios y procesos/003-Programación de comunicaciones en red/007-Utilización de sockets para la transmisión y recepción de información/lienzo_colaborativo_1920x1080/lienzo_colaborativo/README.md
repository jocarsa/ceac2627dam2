# Lienzo colaborativo 1920 × 1080

Pizarra compartida en tiempo real mediante Python, WebSockets y Canvas 2D.

## Instalar

```bash
python3 -m pip install -r requirements.txt
```

## Ejecutar

Terminal 1:
```bash
python3 servidor.py
```

Terminal 2:
```bash
python3 -m http.server 8000
```

Visita http://localhost:8000 desde varios navegadores o dispositivos de la misma red usando http://IP_DEL_SERVIDOR:8000.

El navegador conecta a ws://IP_DEL_SERVIDOR:8765 (o wss en páginas HTTPS, que requiere proxy TLS). Abre los puertos 8000 y 8765 en el cortafuegos si hace falta.

## Funciones

- Lienzo de resolución fija 1920×1080 escalado a la pantalla.
- Pincel, goma, línea, rectángulo, elipse, colores, grosor 1–100.
- Dibujo compartido en tiempo real, contador de usuarios, exportar PNG.
- Deshacer el último trazo propio (Ctrl+Z).
- Historial persistente en `lienzo.sqlite3`; nuevos usuarios recuperan el dibujo.
- Compatible con ratón y pantalla táctil.

## Nota

Es un prototipo educativo: no incorpora autenticación, límites de almacenamiento ni moderación. El borrador pinta blanco. Para borrar todo el lienzo con el servidor detenido, elimina `lienzo.sqlite3`.
