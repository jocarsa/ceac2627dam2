# Maestro / Esclavos

Ejemplo didáctico de computación distribuida usando:

- HTML
- JavaScript
- Web Workers
- PHP
- CSV/JSON
- flock()

## Instalación

Copiar todos los archivos a una carpeta servida por Apache/PHP.

Por ejemplo:

    /var/www/html/distribuido/

Asegurarse de que PHP puede escribir en la carpeta para crear `cola.json`.

## Uso

1. Abrir `index.html` en un ordenador y pulsar **Maestro**.
2. Elegir tamaño de paquete e iteraciones.
3. Pulsar **Preparar trabajo**.
4. Abrir la misma URL desde otros ordenadores.
5. En cada uno pulsar **Esclavo**.

Los esclavos solicitan automáticamente un paquete, lo calculan, entregan
el resultado y solicitan el siguiente.

## Exclusión mutua

`trabajo.php` usa `flock(..., LOCK_EX)` mientras selecciona un paquete
pendiente y lo cambia a `asignado`.

Por eso dos peticiones concurrentes no pueden reservar el mismo paquete.

## Carga

El valor de iteraciones controla el trabajo artificial realizado por
cada paquete.

Empieza con 50.000.000 y ajusta según los equipos.

## Nota

Este proyecto está pensado como demostración didáctica en equipos que
controlas. El cálculo consume CPU intencionadamente mientras un navegador
está actuando como esclavo.
