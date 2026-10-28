# Universo de entidades — PHP + SQLite

Requisitos: PHP 8.1+ con pdo_sqlite y sqlite3; servidor Apache o Nginx con PHP.

1. Copia el contenido del ZIP a una carpeta pública del servidor PHP.
2. Da permisos de escritura al usuario de PHP sobre `data/` (por ejemplo `sudo chown -R www-data:www-data data`).
3. Abre `index.html` desde la URL del servidor, nunca mediante `file://`.
4. En la primera visita se importa el proyecto que esté guardado en localStorage, si existe. Si el servidor ya contiene proyectos, estos prevalecen.

`data/application.sqlite` guarda proyectos, posiciones, propiedades de diseño, categorías, enlaces y preferencias. `data/project_<id>.sqlite` contiene las tablas de datos reales de cada proyecto. Las relaciones id → campo se crean como claves foráneas en SQLite. Las propiedades con formato `nombre: TIPO(longitud)` se convierten a afinidades SQLite (INTEGER, REAL, TEXT, BLOB).

**Importante:** protege `data/` de descargas HTTP; se incluye `.htaccess` para Apache, pero en Nginx debes bloquear la ruta. La sincronización guarda el estado completo, por lo que no está diseñada para edición concurrente entre varios usuarios. Cambiar una tabla o un campo puede provocar migración y pérdida de datos de columnas eliminadas. Haz copias de seguridad antes de cambios estructurales. No hay autenticación: restringe el acceso si se publica en Internet.
