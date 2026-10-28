# Corrección de duplicados SQLite

Se ha corregido `universo/api/index.php`.

- Si una tabla ya existe, guardar el diagrama no vuelve a insertar los registros enviados por el navegador (que podrían estar obsoletos).
- Si una tabla se crea por primera vez, se importan las filas iniciales sin fallar ante claves duplicadas.
- Los registros gestionados por Darkorange permanecen en SQLite.

**Atención:** si el esquema cambia, el mecanismo de migración de tablas existente sigue reconstruyéndolas. Haz copia de seguridad antes de modificar columnas o relaciones.

Sustituye `universo/api/index.php` en tu instalación.
