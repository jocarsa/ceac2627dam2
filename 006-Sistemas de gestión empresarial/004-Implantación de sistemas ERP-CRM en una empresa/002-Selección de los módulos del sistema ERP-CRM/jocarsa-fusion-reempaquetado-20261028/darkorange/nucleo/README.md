# darkorange — componentes C/R

Se han extraído dos componentes reutilizables a `nucleo/`:

- `formulario.js`: componente **C (Create)**. Recibe tabla + columnas, omite PK/id, genera controles y envía JSON a la API.
- `tabla.js`: componente **R (Read)**. Recibe tabla + columnas + registros y construye la tabla.

`codigo.js` queda como orquestador: descubre las entidades, pide `ruta=tabla` y monta ambos componentes para cualquier tabla SQLite.

La API valida siempre el nombre de tabla contra `sqlite_master` y filtra los campos recibidos contra `PRAGMA table_info`, por lo que no depende de nombres concretos como clientes/empleados/productos.
