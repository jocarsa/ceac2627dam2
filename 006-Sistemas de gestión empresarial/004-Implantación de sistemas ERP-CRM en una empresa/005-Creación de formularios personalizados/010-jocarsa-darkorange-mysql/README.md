# jocarsa | darkorange · MySQL

Requiere PHP 8.1+, extensiones pdo_mysql y MySQL 8.0.16+.

1. `sudo mysql < sql/jocarsa.sql`
2. `sudo mysql < sql/usuario.sql`
3. Copiar este directorio al DocumentRoot de Apache con PHP habilitado.
4. Abrir `index.html` desde el servidor (no mediante file://).

Credenciales predeterminadas de demostración: base `jocarsa`, usuario `jocarsa`, contraseña `jocarsa`. Configuración en `clases/Conexion.php`, sobrescribible mediante `JOCARSA_DB_HOST`, `JOCARSA_DB_NAME`, `JOCARSA_DB_USER`, `JOCARSA_DB_PASSWORD`. Cambiar la contraseña antes de publicar.

La interfaz conserva los estilos darkorange y solicita vistas HTML renderizadas en servidor: `Tabla` y `Grafica` heredan de `Vista`; todos los formularios se producen con la clase `Formularios` entregada. Se recuperan tipos de columnas y relaciones mediante `information_schema`; se usa PDO con sentencias preparadas para inserciones. Las consultas de tablas están limitadas a 200 filas para evitar saturación.

**Limitaciones:** no se ha probado contra un servidor MySQL real; el esquema proporcionado puede contener incompatibilidades con versiones de MariaDB. La interfaz actual permite consultar e insertar, no editar ni eliminar. Los controles de clave foránea presentan identificadores. Los tipos espaciales, JSON, BLOB y BIT requieren validación/conversión adicional para una edición completa. Las fechas, campos de texto y algunas opciones de `Formularios2.php` conservan el comportamiento de la clase original. La aplicación no incorpora autenticación ni CSRF: **no exponer en Internet sin añadir estas protecciones**. No se incluyen los módulos de edición de diagramas de Universo, que requieren una migración independiente de su almacenamiento SQLite.
