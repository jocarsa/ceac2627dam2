text
number
date
time
color
rango
select - enumeracion
progress - valor
checkbox - enum multiple
radio - enum multiple unica
datalist enumeracion
textarea - texto grande

1. Tipos numéricos enteros
Tipo	Tamaño	Descripción
TINYINT	1 byte	Entero muy pequeño
SMALLINT	2 bytes	Entero pequeño
MEDIUMINT	3 bytes	Entero mediano
INT / INTEGER	4 bytes	Entero estándar
BIGINT	8 bytes	Entero grande
BOOL / BOOLEAN	1 byte	Alias de TINYINT(1)

Los enteros admiten SIGNED (con signo) y UNSIGNED (sin signo).
2. Tipos numéricos decimales
Tipo	Descripción
FLOAT	Decimal de precisión aproximada simple
DOUBLE	Decimal de precisión aproximada doble
DOUBLE PRECISION	Sinónimo de DOUBLE
REAL	Normalmente sinónimo de DOUBLE
DECIMAL(M,D)	Decimal exacto de precisión definida
NUMERIC(M,D)	Sinónimo de DECIMAL

Para almacenar precios y cantidades monetarias, normalmente se utiliza DECIMAL(10,2).
3. Tipos de cadenas de texto
Tipo	Descripción
CHAR(n)	Cadena de longitud fija
VARCHAR(n)	Cadena de longitud variable
TINYTEXT	Texto de hasta 255 bytes
TEXT	Texto de hasta 65.535 bytes
MEDIUMTEXT	Texto de hasta 16 MB aproximadamente
LONGTEXT	Texto de hasta 4 GB aproximadamente
ENUM	Un valor de una lista predefinida
SET	Varios valores de una lista predefinida

4. Tipos de fecha y hora
Tipo	Formato habitual	Descripción
DATE	YYYY-MM-DD	Fecha
TIME	HH:MM:SS	Hora o duración
DATETIME	YYYY-MM-DD HH:MM:SS	Fecha y hora
TIMESTAMP	YYYY-MM-DD HH:MM:SS	Marca temporal con conversión de zona horaria
YEAR	YYYY	Año

5. Tipos binarios
Tipo	Descripción
BINARY(n)	Datos binarios de longitud fija
VARBINARY(n)	Datos binarios de longitud variable
TINYBLOB	Binario de hasta 255 bytes
BLOB	Binario de hasta 65.535 bytes
MEDIUMBLOB	Binario de hasta 16 MB aproximadamente
LONGBLOB	Binario de hasta 4 GB aproximadamente
BIT(n)	Campo de bits

6. Tipos espaciales (GIS)
Tipo	Descripción
GEOMETRY	Geometría genérica
POINT	Punto
LINESTRING	Línea
POLYGON	Polígono
MULTIPOINT	Conjunto de puntos
MULTILINESTRING	Conjunto de líneas
MULTIPOLYGON	Conjunto de polígonos
GEOMETRYCOLLECTION	Colección de geometrías

7. Tipos JSON
Tipo	Descripción
JSON	Documentos JSON

Diferencia importante: MySQL almacena JSON en un formato binario interno optimizado. MariaDB implementa JSON como alias de LONGTEXT, con validación JSON según la definición y versión.
8. Tipos especiales y diferencias entre motores
Tipo	Motor	Descripción
INET4	MariaDB	Dirección IPv4
INET6	MariaDB	Dirección IPv6
UUID	MariaDB	Identificador UUID nativo
VECTOR(N)	MariaDB reciente	Vector numérico para búsquedas de similitud
SERIAL	Ambos	Alias para entero grande sin signo autoincremental con restricción de unicidad

Algunos tipos especiales dependen de la versión concreta de MySQL o MariaDB.