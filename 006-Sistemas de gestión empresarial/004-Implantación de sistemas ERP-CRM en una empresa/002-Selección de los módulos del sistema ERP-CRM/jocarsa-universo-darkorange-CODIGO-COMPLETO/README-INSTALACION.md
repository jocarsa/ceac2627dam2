# jocarsa | Universo + Darkorange

## Instalación
Copiar las carpetas `universo` y `darkorange` juntas en el mismo directorio web (Apache + PHP SQLite3 + PDO SQLite).
Abrir `universo/index.html`, crear/guardar el proyecto y después abrir `darkorange/index.html`.
El ERP utiliza directamente `universo/data/<nombre del proyecto>.sqlite`; los módulos se derivan de `categories_json` de `universo/data/application.sqlite`.

**Importante:** Hacer copia de seguridad de las bases de datos antes de actualizar. El diseñador original reconstruye tablas cuando cambia el esquema; no cambiar estructuras en producción sin respaldo. Esta versión elimina el borrado masivo de registros y tablas al guardar, pero las migraciones de columnas pueden requerir una migración controlada. No publicar sin autenticación y control de permisos.

Los informes y dashboards existentes se conservan, pero algunas vistas pueden necesitar ajustes adicionales según el esquema concreto de cada proyecto.
