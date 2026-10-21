PRAGMA foreign_keys = ON;

CREATE TABLE clientes(
    nombre TEXT,
    pais TEXT,
    telefono TEXT,
    email TEXT,
    identificador INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE productos(
    nombre TEXT,
    tipo TEXT,
    precio REAL,
    capacidad INTEGER,
    autonomia INTEGER,
    identificador INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE empleados(
    nombre TEXT,
    apellidos TEXT,
    departamento TEXT,
    puesto TEXT,
    salario REAL,
    identificador INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE proveedores(
    nombre TEXT,
    pais TEXT,
    especialidad TEXT,
    email TEXT,
    identificador INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE pedidos(
    fecha TEXT,
    estado TEXT,
    cliente_id INTEGER,
    total REAL,
    identificador INTEGER PRIMARY KEY AUTOINCREMENT,
    FOREIGN KEY(cliente_id) REFERENCES clientes(identificador)
);

CREATE TABLE lineaspedido(
    pedido_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER,
    precio_unitario REAL,
    identificador INTEGER PRIMARY KEY AUTOINCREMENT,
    FOREIGN KEY(pedido_id) REFERENCES pedidos(identificador),
    FOREIGN KEY(producto_id) REFERENCES productos(identificador)
);

CREATE TABLE componentes(
    nombre TEXT,
    tipo TEXT,
    proveedor_id INTEGER,
    precio REAL,
    stock INTEGER,
    identificador INTEGER PRIMARY KEY AUTOINCREMENT,
    FOREIGN KEY(proveedor_id) REFERENCES proveedores(identificador)
);