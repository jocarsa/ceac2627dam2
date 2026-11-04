-- Jocarsa | Empresa - MySQL 8.0.16+
-- Datos ficticios de demostración. UTF8MB4.
CREATE DATABASE IF NOT EXISTS jocarsa_empresa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE jocarsa_empresa;

CREATE TABLE IF NOT EXISTS empresas (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 codigo CHAR(8) NOT NULL UNIQUE,
 nombre VARCHAR(150) NOT NULL,
 nombre_comercial VARCHAR(150),
 descripcion MEDIUMTEXT,
 historia LONGTEXT,
 sector ENUM('software','formacion','consultoria','diseno','otros') NOT NULL DEFAULT 'software',
 servicios SET('desarrollo','docencia','3d','infraestructura','ia','consultoria'),
 activa BOOLEAN NOT NULL DEFAULT TRUE,
 empleados_estimados SMALLINT UNSIGNED DEFAULT 0,
 proyectos_estimados MEDIUMINT UNSIGNED DEFAULT 0,
 fecha_fundacion DATE,
 hora_apertura TIME,
 actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 creado DATETIME DEFAULT CURRENT_TIMESTAMP,
 ejercicio_inicio YEAR,
 logo VARBINARY(255),
 sello BINARY(16),
 CONSTRAINT chk_empresa_empleados CHECK (empleados_estimados <= 10000)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clientes (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 empresa_id BIGINT UNSIGNED NOT NULL,
 codigo CHAR(10) NOT NULL UNIQUE,
 nombre VARCHAR(150) NOT NULL,
 email VARCHAR(254),
 telefono VARCHAR(30),
 nif CHAR(9),
 tipo ENUM('particular','empresa','centro_educativo','administracion') NOT NULL,
 intereses SET('erp','crm','web','ia','formacion','3d','hosting'),
 prioridad TINYINT UNSIGNED NOT NULL DEFAULT 3,
 empleados SMALLINT UNSIGNED DEFAULT 0,
 presupuesto DECIMAL(12,2) UNSIGNED DEFAULT 0.00,
 descuento NUMERIC(5,2) DEFAULT 0.00,
 puntuacion FLOAT DEFAULT 0,
 potencial DOUBLE DEFAULT 0,
 riesgo REAL DEFAULT 0,
 notas TEXT,
 fecha_alta DATE DEFAULT (CURRENT_DATE),
 ultima_llamada DATETIME,
 acepta_comunicaciones BOOL DEFAULT FALSE,
 FOREIGN KEY (empresa_id) REFERENCES empresas(id),
 CONSTRAINT chk_cliente_prioridad CHECK (prioridad BETWEEN 1 AND 5),
 CONSTRAINT chk_cliente_descuento CHECK (descuento BETWEEN 0 AND 100),
 CONSTRAINT chk_cliente_puntuacion CHECK (puntuacion BETWEEN 0 AND 10)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS empleados (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 empresa_id BIGINT UNSIGNED NOT NULL,
 nombre VARCHAR(120) NOT NULL,
 email VARCHAR(254) UNIQUE,
 rol ENUM('administracion','desarrollo','docencia','diseno','soporte','direccion') NOT NULL,
 competencias SET('php','python','javascript','sql','3d','linux','ia','redes'),
 jornada_horas TINYINT UNSIGNED DEFAULT 40,
 antiguedad_meses SMALLINT UNSIGNED DEFAULT 0,
 salario DECIMAL(10,2) UNSIGNED,
 productividad FLOAT DEFAULT 0,
 fecha_incorporacion DATE,
 hora_entrada TIME,
 remoto BOOLEAN DEFAULT FALSE,
 observaciones TINYTEXT,
 FOREIGN KEY (empresa_id) REFERENCES empresas(id),
 CONSTRAINT chk_empleado_jornada CHECK (jornada_horas BETWEEN 1 AND 60),
 CONSTRAINT chk_empleado_productividad CHECK (productividad BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS productos (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 empresa_id BIGINT UNSIGNED NOT NULL,
 sku CHAR(12) NOT NULL UNIQUE,
 nombre VARCHAR(150) NOT NULL,
 descripcion_corta TINYTEXT,
 descripcion TEXT,
 documentacion MEDIUMTEXT,
 manual_completo LONGTEXT,
 categoria ENUM('erp','crm','educacion','ia','infraestructura','web','utilidad') NOT NULL,
 plataformas SET('web','linux','windows','android','ios','api'),
 estado ENUM('idea','desarrollo','beta','publicado','mantenimiento','retirado') NOT NULL,
 version CHAR(12),
 precio DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT 0,
 coste_estimado NUMERIC(12,2) UNSIGNED DEFAULT 0,
 descuento DECIMAL(5,2) DEFAULT 0,
 usuarios_activos MEDIUMINT UNSIGNED DEFAULT 0,
 descargas BIGINT UNSIGNED DEFAULT 0,
 valoracion FLOAT DEFAULT 0,
 carga_media DOUBLE DEFAULT 0,
 consumo_memoria REAL DEFAULT 0,
 color CHAR(7),
 fecha_lanzamiento DATE,
 ultima_revision TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 codigo_fuente LONGBLOB,
 miniatura MEDIUMBLOB,
 icono TINYBLOB,
 banderas BIT(8) NOT NULL DEFAULT b'00000000',
 FOREIGN KEY (empresa_id) REFERENCES empresas(id),
 CONSTRAINT chk_producto_descuento CHECK (descuento BETWEEN 0 AND 100),
 CONSTRAINT chk_producto_valoracion CHECK (valoracion BETWEEN 0 AND 5)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS proyectos (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 empresa_id BIGINT UNSIGNED NOT NULL,
 cliente_id BIGINT UNSIGNED,
 producto_id BIGINT UNSIGNED,
 responsable_id BIGINT UNSIGNED,
 codigo CHAR(10) UNIQUE NOT NULL,
 titulo VARCHAR(180) NOT NULL,
 requisitos LONGTEXT,
 especificacion MEDIUMTEXT,
 estado ENUM('propuesto','planificado','activo','pausado','finalizado','cancelado') DEFAULT 'propuesto',
 tecnologias SET('php','python','javascript','mysql','sqlite','c','ollama','docker','html','css'),
 prioridad TINYINT UNSIGNED DEFAULT 3,
 progreso DECIMAL(5,2) UNSIGNED DEFAULT 0,
 horas_estimadas DECIMAL(9,2) UNSIGNED DEFAULT 0,
 horas_reales FLOAT DEFAULT 0,
 presupuesto DECIMAL(12,2) UNSIGNED DEFAULT 0,
 inicio DATE,
 entrega DATE,
 fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (empresa_id) REFERENCES empresas(id),
 FOREIGN KEY (cliente_id) REFERENCES clientes(id),
 FOREIGN KEY (producto_id) REFERENCES productos(id),
 FOREIGN KEY (responsable_id) REFERENCES empleados(id),
 CONSTRAINT chk_proyecto_prioridad CHECK (prioridad BETWEEN 1 AND 5),
 CONSTRAINT chk_proyecto_progreso CHECK (progreso BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tareas (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 proyecto_id BIGINT UNSIGNED NOT NULL,
 asignado_id BIGINT UNSIGNED,
 titulo VARCHAR(180) NOT NULL,
 detalle TEXT,
 estado ENUM('pendiente','en_curso','revision','completada','bloqueada') DEFAULT 'pendiente',
 etiquetas SET('backend','frontend','seguridad','bbdd','ui','testing','documentacion'),
 prioridad TINYINT UNSIGNED DEFAULT 3,
 horas DECIMAL(7,2) UNSIGNED DEFAULT 0,
 fecha_limite DATETIME,
 completada BOOLEAN DEFAULT FALSE,
 FOREIGN KEY (proyecto_id) REFERENCES proyectos(id),
 FOREIGN KEY (asignado_id) REFERENCES empleados(id),
 CONSTRAINT chk_tarea_prioridad CHECK (prioridad BETWEEN 1 AND 5)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ventas (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 cliente_id BIGINT UNSIGNED NOT NULL,
 producto_id BIGINT UNSIGNED NOT NULL,
 comercial_id BIGINT UNSIGNED,
 referencia CHAR(12) NOT NULL UNIQUE,
 unidades SMALLINT UNSIGNED NOT NULL DEFAULT 1,
 precio_unitario DECIMAL(10,2) UNSIGNED NOT NULL,
 descuento DECIMAL(5,2) UNSIGNED DEFAULT 0,
 iva DECIMAL(5,2) UNSIGNED DEFAULT 21,
 estado ENUM('borrador','presupuesto','aceptada','facturada','cancelada') DEFAULT 'borrador',
 canales SET('web','email','telefono','presencial'),
 fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
 total DECIMAL(12,2) GENERATED ALWAYS AS (ROUND(unidades * precio_unitario * (1 - descuento / 100) * (1 + iva / 100),2)) STORED,
 FOREIGN KEY (cliente_id) REFERENCES clientes(id),
 FOREIGN KEY (producto_id) REFERENCES productos(id),
 FOREIGN KEY (comercial_id) REFERENCES empleados(id),
 CONSTRAINT chk_venta_descuento CHECK (descuento BETWEEN 0 AND 100),
 CONSTRAINT chk_venta_iva CHECK (iva BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS facturas (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 venta_id BIGINT UNSIGNED NOT NULL UNIQUE,
 numero VARCHAR(30) NOT NULL UNIQUE,
 emitida DATE NOT NULL,
 vencimiento DATE,
 pagada BOOLEAN DEFAULT FALSE,
 forma_pago ENUM('transferencia','tarjeta','efectivo','domiciliacion','otro') DEFAULT 'transferencia',
 observaciones TEXT,
 pdf LONGBLOB,
 FOREIGN KEY (venta_id) REFERENCES ventas(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS centros_formacion (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 empresa_id BIGINT UNSIGNED NOT NULL,
 nombre VARCHAR(160) NOT NULL,
 localidad VARCHAR(100),
 modalidad SET('presencial','online','semipresencial'),
 descripcion TEXT,
 FOREIGN KEY (empresa_id) REFERENCES empresas(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cursos (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 centro_id INT UNSIGNED NOT NULL,
 codigo CHAR(10) NOT NULL UNIQUE,
 nombre VARCHAR(160) NOT NULL,
 familia ENUM('DAM','DAW','SMR','ASIR','IA','OTROS') NOT NULL,
 horas SMALLINT UNSIGNED NOT NULL,
 contenidos LONGTEXT,
 inicio DATE,
 fin DATE,
 modalidad ENUM('presencial','online','hibrida'),
 FOREIGN KEY (centro_id) REFERENCES centros_formacion(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS alumnos (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 nombre VARCHAR(140) NOT NULL,
 email VARCHAR(254) UNIQUE,
 telefono VARCHAR(30),
 fecha_nacimiento DATE,
 consentimiento BOOLEAN DEFAULT FALSE,
 preferencias SET('backend','frontend','sistemas','ia','3d'),
 avatar BLOB,
 observaciones TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS matriculas (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 alumno_id BIGINT UNSIGNED NOT NULL,
 curso_id INT UNSIGNED NOT NULL,
 fecha DATE NOT NULL,
 estado ENUM('activa','finalizada','anulada') DEFAULT 'activa',
 calificacion DECIMAL(4,2),
 asistencia DECIMAL(5,2) UNSIGNED DEFAULT 0,
 aprobado BOOL DEFAULT FALSE,
 UNIQUE (alumno_id,curso_id),
 FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
 FOREIGN KEY (curso_id) REFERENCES cursos(id),
 CONSTRAINT chk_matricula_nota CHECK (calificacion BETWEEN 0 AND 10),
 CONSTRAINT chk_matricula_asistencia CHECK (asistencia BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS servidores (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 empresa_id BIGINT UNSIGNED NOT NULL,
 hostname VARCHAR(120) NOT NULL UNIQUE,
 ip VARCHAR(45),
 sistema ENUM('ubuntu','debian','windows','otro') NOT NULL,
 servicios SET('apache','nginx','mysql','sqlite','ollama','mediasoup','flask','php'),
 nucleos TINYINT UNSIGNED,
 ram_gb SMALLINT UNSIGNED,
 disco_gb MEDIUMINT UNSIGNED,
 ancho_banda_mbps INT UNSIGNED,
 uptime_segundos BIGINT UNSIGNED DEFAULT 0,
 carga_cpu FLOAT DEFAULT 0,
 temperatura DOUBLE DEFAULT 0,
 disponible BOOLEAN DEFAULT TRUE,
 ultima_revision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (empresa_id) REFERENCES empresas(id),
 CONSTRAINT chk_servidor_cpu CHECK (carga_cpu BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS incidencias (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 servidor_id INT UNSIGNED,
 proyecto_id BIGINT UNSIGNED,
 titulo VARCHAR(180) NOT NULL,
 detalle MEDIUMTEXT,
 severidad ENUM('baja','media','alta','critica') DEFAULT 'media',
 sintomas SET('http_500','http_401','http_404','sqlite_lock','memoria','red','otro'),
 estado ENUM('abierta','investigando','resuelta','cerrada') DEFAULT 'abierta',
 detectada DATETIME DEFAULT CURRENT_TIMESTAMP,
 resuelta DATETIME,
 log_archivo LONGBLOB,
 FOREIGN KEY (servidor_id) REFERENCES servidores(id),
 FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
) ENGINE=InnoDB;

-- Tabla pedagógica: todos los tamaños enteros, decimales, textos, binarios y fechas.
CREATE TABLE IF NOT EXISTS laboratorio_tipos (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 entero_tiny TINYINT,
 entero_tiny_unsigned TINYINT UNSIGNED,
 entero_small SMALLINT,
 entero_small_unsigned SMALLINT UNSIGNED,
 entero_medium MEDIUMINT,
 entero_medium_unsigned MEDIUMINT UNSIGNED,
 entero_int INT,
 entero_int_unsigned INT UNSIGNED,
 entero_big BIGINT,
 entero_big_unsigned BIGINT UNSIGNED,
 booleano BOOLEAN,
 decimal_float FLOAT,
 decimal_double DOUBLE,
 decimal_double_precision DOUBLE PRECISION,
 decimal_real REAL,
 decimal_exacto DECIMAL(10,2),
 decimal_numerico NUMERIC(8,3),
 cadena_char CHAR(12),
 cadena_varchar VARCHAR(120),
 cadena_tinytext TINYTEXT,
 cadena_text TEXT,
 cadena_mediumtext MEDIUMTEXT,
 cadena_longtext LONGTEXT,
 opcion_enum ENUM('primera','segunda','tercera'),
 opciones_set SET('php','python','sql','javascript'),
 fecha DATE,
 hora TIME,
 fecha_hora DATETIME,
 marca_tiempo TIMESTAMP NULL,
 anio YEAR,
 binario_fijo BINARY(16),
 binario_variable VARBINARY(255),
 archivo_tiny TINYBLOB,
 archivo_blob BLOB,
 archivo_medium MEDIUMBLOB,
 archivo_long LONGBLOB,
 bits BIT(8),
 CONSTRAINT chk_lab_float CHECK (decimal_float BETWEEN -1000 AND 1000),
 CONSTRAINT chk_lab_decimal CHECK (decimal_exacto BETWEEN -9999.99 AND 9999.99)
) ENGINE=InnoDB;

-- Metadatos adicionales para un generador de formularios basado en INFORMATION_SCHEMA.
-- Los límites nativos de los tipos se infieren; esta tabla expresa reglas de negocio/UX.
CREATE TABLE IF NOT EXISTS formulario_campos (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 tabla VARCHAR(64) NOT NULL,
 columna VARCHAR(64) NOT NULL,
 etiqueta VARCHAR(160),
 control_html ENUM('auto','number','text','radio','checkbox','date','time','datetime-local','file','textarea') NOT NULL DEFAULT 'auto',
 minimo DECIMAL(30,10) NULL,
 maximo DECIMAL(30,10) NULL,
 paso DECIMAL(20,10) NULL,
 longitud_maxima BIGINT UNSIGNED NULL,
 tamano_archivo_max BIGINT UNSIGNED NULL,
 extensiones_permitidas VARCHAR(255) NULL,
 obligatorio BOOLEAN DEFAULT FALSE,
 ayuda TEXT,
 UNIQUE(tabla,columna)
) ENGINE=InnoDB;

INSERT INTO empresas (codigo,nombre,nombre_comercial,descripcion,historia,sector,servicios,activa,empleados_estimados,proyectos_estimados,fecha_fundacion,hora_apertura,ejercicio_inicio,sello)
VALUES ('JOCARSA1','Jocarsa','jocarsa','Desarrollo de software, formación, IA e infraestructura','Empresa ficticia de demostración inspirada en líneas de actividad de Jocarsa.','software','desarrollo,docencia,3d,infraestructura,ia,consultoria',TRUE,6,25,'2005-01-01','09:00:00',2005,UNHEX('00112233445566778899AABBCCDDEEFF'));

INSERT INTO clientes (empresa_id,codigo,nombre,email,tipo,intereses,prioridad,empleados,presupuesto,descuento,puntuacion,potencial,riesgo,notas)
VALUES
(1,'CLI0000001','Centro de Formación Demo','contacto@centro-demo.example','centro_educativo','erp,formacion,web',5,40,18000,5,8.5,0.85,0.12,'Cliente ficticio'),
(1,'CLI0000002','Soluciones Digitales Demo','hola@digital-demo.example','empresa','crm,ia,hosting',3,12,9500,0,7.2,0.65,0.25,'Cliente ficticio');

INSERT INTO empleados (empresa_id,nombre,email,rol,competencias,jornada_horas,antiguedad_meses,salario,productividad,fecha_incorporacion,hora_entrada,remoto,observaciones)
VALUES
(1,'Responsable Demo','responsable@jocarsa-demo.example','direccion','python,php,sql,linux,ia',40,120,3200,88,'2016-09-01','09:00:00',TRUE,'Datos ficticios'),
(1,'Desarrolladora Demo','dev@jocarsa-demo.example','desarrollo','javascript,php,sql',38,24,2300,91,'2024-10-01','08:30:00',TRUE,'Datos ficticios');

INSERT INTO productos (empresa_id,sku,nombre,descripcion_corta,descripcion,documentacion,manual_completo,categoria,plataformas,estado,version,precio,coste_estimado,descuento,usuarios_activos,descargas,valoracion,carga_media,consumo_memoria,color,fecha_lanzamiento,icono,banderas)
VALUES
(1,'JOC-ERP-0001','jocarsa | erp','Gestión empresarial modular','ERP con entidades, permisos, importación y APIs','Documentación de ejemplo','Manual de demostración','erp','web,linux,api','desarrollo','0.9.0',249.00,1200.00,0,35,100,4.6,0.12,250.5,'#8B4513','2026-10-01',X'89504E47',b'00000101'),
(1,'JOC-CRM-0001','jocarsa | ventas','CRM y pipeline comercial','Cuentas, campañas, contactos y ventas','Documentación de ejemplo','Manual de demostración','crm','web,api','beta','0.8.0',149.00,850.00,10,25,75,4.4,0.10,180.0,'#F4A460','2026-10-10',X'89504E47',b'00000011'),
(1,'JOC-EDU-0001','jocarsa | calificaciones','Gestión de calificaciones','Grupos, asignaturas, evaluaciones y auditoría','Documentación de ejemplo','Manual de demostración','educacion','web','publicado','1.0.0',99.00,600.00,0,250,500,4.8,0.08,120.0,'#87CEFA','2026-11-01',X'89504E47',b'00000001'),
(1,'JOC-IA-00001','jocarsa | ia','Conversaciones y proyectos con IA','Asistente local conectado con Ollama','Documentación de ejemplo','Manual de demostración','ia','web,linux,api','desarrollo','0.4.0',79.00,400.00,0,15,40,4.2,0.45,2048.0,'#87CEFA','2026-11-03',X'89504E47',b'00000111');

INSERT INTO proyectos (empresa_id,cliente_id,producto_id,responsable_id,codigo,titulo,requisitos,especificacion,estado,tecnologias,prioridad,progreso,horas_estimadas,horas_reales,presupuesto,inicio,entrega)
VALUES
(1,1,1,1,'PROY000001','ERP integrado','Permisos, entidades y formularios','Backend PHP y MySQL','activo','php,javascript,mysql,html,css',5,75.00,240,180,18000,'2026-10-01','2026-12-15'),
(1,2,4,2,'PROY000002','Plataforma de IA','Conversaciones, proyectos y biblioteca','Ollama y persistencia','activo','python,ollama,sqlite,html,css',4,45.00,160,70,9500,'2026-11-01','2027-01-20');

INSERT INTO tareas (proyecto_id,asignado_id,titulo,detalle,estado,etiquetas,prioridad,horas,fecha_limite,completada)
VALUES (1,2,'Generador de formularios','Inferir HTML desde INFORMATION_SCHEMA','en_curso','backend,bbdd,ui',5,12,'2026-11-20 18:00:00',FALSE),
(2,1,'Streaming de respuestas','Mostrar código y vista previa incrementalmente','pendiente','backend,frontend',4,8,'2026-11-25 18:00:00',FALSE);

INSERT INTO ventas (cliente_id,producto_id,comercial_id,referencia,unidades,precio_unitario,descuento,iva,estado,canales,fecha)
VALUES (1,1,1,'VEN202600001',2,249.00,5,21,'facturada','email,web','2026-11-02 10:00:00'),
(2,2,1,'VEN202600002',1,149.00,0,21,'aceptada','telefono','2026-11-03 12:00:00');
INSERT INTO facturas (venta_id,numero,emitida,vencimiento,pagada,forma_pago,observaciones)
VALUES (1,'F-2026-0001','2026-11-02','2026-12-02',FALSE,'transferencia','Factura de demostración');

INSERT INTO centros_formacion (empresa_id,nombre,localidad,modalidad,descripcion)
VALUES (1,'Centro FP Demo Valencia','Valencia','presencial,online','Centro ficticio para ejemplos educativos');
INSERT INTO cursos (centro_id,codigo,nombre,familia,horas,contenidos,inicio,fin,modalidad)
VALUES (1,'DAM2026001','Desarrollo de Aplicaciones Multiplataforma','DAM',2000,'Python, Java, bases de datos, interfaces','2026-09-01','2027-06-30','hibrida'),
(1,'DAW2026001','Desarrollo de Aplicaciones Web','DAW',2000,'HTML, CSS, JavaScript, PHP, SQL','2026-09-01','2027-06-30','presencial');
INSERT INTO alumnos (nombre,email,fecha_nacimiento,consentimiento,preferencias,observaciones)
VALUES ('Alumna Demo Uno','alumna1@example.test','2003-05-12',TRUE,'backend,ia','Registro ficticio'),
('Alumno Demo Dos','alumno2@example.test','2002-08-19',TRUE,'frontend,sistemas','Registro ficticio');
INSERT INTO matriculas (alumno_id,curso_id,fecha,estado,calificacion,asistencia,aprobado)
VALUES (1,1,'2026-09-01','activa',8.50,94.00,TRUE),(2,2,'2026-09-01','activa',7.25,89.00,TRUE);

INSERT INTO servidores (empresa_id,hostname,ip,sistema,servicios,nucleos,ram_gb,disco_gb,ancho_banda_mbps,uptime_segundos,carga_cpu,temperatura,disponible)
VALUES (1,'vps-demo.jocarsa.example','192.0.2.10','ubuntu','apache,mysql,mediasoup,php',8,16,250,1000,120000,28.5,47.2,TRUE),
(1,'ia-demo.jocarsa.example','192.0.2.11','ubuntu','ollama,flask,sqlite',16,32,1000,1000,350000,65.0,58.3,TRUE);
INSERT INTO incidencias (servidor_id,proyecto_id,titulo,detalle,severidad,sintomas,estado,detectada,resuelta)
VALUES (1,1,'Bloqueo SQLite simulado','Ejemplo de contención de escritura','alta','sqlite_lock','resuelta','2026-10-19 11:00:00','2026-10-19 12:15:00'),
(2,2,'Error HTTP 500 simulado','Ejemplo de error de aplicación','media','http_500','investigando','2026-11-03 15:00:00',NULL);

INSERT INTO laboratorio_tipos (
 entero_tiny,entero_tiny_unsigned,entero_small,entero_small_unsigned,entero_medium,entero_medium_unsigned,entero_int,entero_int_unsigned,entero_big,entero_big_unsigned,booleano,
 decimal_float,decimal_double,decimal_double_precision,decimal_real,decimal_exacto,decimal_numerico,
 cadena_char,cadena_varchar,cadena_tinytext,cadena_text,cadena_mediumtext,cadena_longtext,
 opcion_enum,opciones_set,fecha,hora,fecha_hora,marca_tiempo,anio,
 binario_fijo,binario_variable,archivo_tiny,archivo_blob,archivo_medium,archivo_long,bits
) VALUES (
 -12,250,-32000,65000,-8000000,16000000,-2000000000,4000000000,-9000000000000000000,18000000000000000000,TRUE,
 12.5,1234.5678,2345.6789,3456.789,1234.56,123.456,
 'JOCARSA','Texto variable','Texto breve','Texto normal','Texto mediano','Texto largo',
 'segunda','php,python,sql','2026-11-04','16:00:00','2026-11-04 16:00:00','2026-11-04 16:00:00',2026,
 UNHEX('00112233445566778899AABBCCDDEEFF'),X'01020304',X'00FF',X'89504E470D0A1A0A',X'25504446',X'504B0304',b'10101010'
);

INSERT INTO formulario_campos (tabla,columna,etiqueta,control_html,minimo,maximo,paso,longitud_maxima,tamano_archivo_max,extensiones_permitidas,obligatorio,ayuda)
VALUES
('clientes','prioridad','Prioridad','number',1,5,1,NULL,NULL,NULL,TRUE,'Entero de 1 a 5'),
('clientes','descuento','Descuento (%)','number',0,100,0.01,NULL,NULL,NULL,FALSE,'Porcentaje de descuento'),
('productos','precio','Precio (€)','number',0,99999999.99,0.01,NULL,NULL,NULL,TRUE,'Importe monetario'),
('productos','categoria','Categoría','radio',NULL,NULL,NULL,NULL,NULL,NULL,TRUE,'Opciones obtenidas del ENUM'),
('productos','plataformas','Plataformas','checkbox',NULL,NULL,NULL,NULL,NULL,NULL,FALSE,'Opciones obtenidas del SET'),
('productos','icono','Icono','file',NULL,NULL,NULL,NULL,255,'image/png,image/jpeg',FALSE,'TINYBLOB: máximo 255 bytes; solo archivos muy pequeños'),
('productos','miniatura','Miniatura','file',NULL,NULL,NULL,NULL,16777215,'image/png,image/jpeg',FALSE,'MEDIUMBLOB: hasta 16 MiB menos un byte'),
('productos','codigo_fuente','Código fuente','file',NULL,NULL,NULL,NULL,10485760,'.zip,.tar,.gz',FALSE,'Límite de negocio: 10 MiB'),
('facturas','pdf','PDF factura','file',NULL,NULL,NULL,NULL,10485760,'application/pdf',FALSE,'Límite de negocio: 10 MiB'),
('laboratorio_tipos','cadena_varchar','Texto variable','text',NULL,NULL,NULL,120,NULL,NULL,FALSE,'VARCHAR(120)'),
('laboratorio_tipos','binario_fijo','Binario fijo','file',NULL,NULL,NULL,NULL,16,NULL,FALSE,'BINARY(16): exige exactamente 16 bytes'),
('laboratorio_tipos','binario_variable','Binario variable','file',NULL,NULL,NULL,NULL,255,NULL,FALSE,'VARBINARY(255): hasta 255 bytes'),
('laboratorio_tipos','archivo_tiny','Archivo pequeño','file',NULL,NULL,NULL,NULL,255,NULL,FALSE,'TINYBLOB'),
('laboratorio_tipos','archivo_blob','Archivo estándar','file',NULL,NULL,NULL,NULL,65535,NULL,FALSE,'BLOB'),
('laboratorio_tipos','archivo_medium','Archivo mediano','file',NULL,NULL,NULL,NULL,16777215,NULL,FALSE,'MEDIUMBLOB'),
('laboratorio_tipos','archivo_long','Archivo grande','file',NULL,NULL,NULL,NULL,10485760,NULL,FALSE,'LONGBLOB admite más; límite práctico demo de 10 MiB'),
('laboratorio_tipos','bits','Bits','file',NULL,NULL,NULL,NULL,1,NULL,FALSE,'BIT(8): un byte; validar bits en servidor');

-- Inspección para el generador de formularios:
-- SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, CHARACTER_MAXIMUM_LENGTH,
--        NUMERIC_PRECISION, NUMERIC_SCALE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_SCHEMA='jocarsa_empresa' AND TABLE_NAME='laboratorio_tipos'
-- ORDER BY ORDINAL_POSITION;
