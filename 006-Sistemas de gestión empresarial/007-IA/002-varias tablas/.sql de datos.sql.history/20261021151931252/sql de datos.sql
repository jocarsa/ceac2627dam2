
-- Activar claves foráneas en SQLite
PRAGMA foreign_keys = ON;

-- ========================================
-- 1. CREAR TABLAS
-- ========================================

DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    ciudad TEXT,
    fecha_registro TEXT
);

CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    modelo TEXT NOT NULL,
    categoria TEXT,
    precio REAL NOT NULL,
    potencia INTEGER,
    autonomia INTEGER,
    stock INTEGER DEFAULT 0
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    precio_venta REAL NOT NULL,
    estado TEXT DEFAULT 'Pendiente',
    FOREIGN KEY (cliente_id)
        REFERENCES clientes(id),
    FOREIGN KEY (producto_id)
        REFERENCES productos(id)
);

-- ========================================
-- 2. INSERTAR CLIENTES
-- ========================================

INSERT INTO clientes
(nombre, apellidos, email, telefono, ciudad, fecha_registro)
VALUES
('Carlos', 'Martínez López', 'carlos@example.com', '600111222', 'Valencia', '2026-01-10'),
('Laura', 'García Pérez', 'laura@example.com', '600222333', 'Madrid', '2026-01-15'),
('Miguel', 'Fernández Ruiz', 'miguel@example.com', '600333444', 'Barcelona', '2026-02-02'),
('Ana', 'Sánchez Torres', 'ana@example.com', '600444555', 'Sevilla', '2026-02-12'),
('David', 'Romero Gil', 'david@example.com', '600555666', 'Alicante', '2026-03-01'),
('Elena', 'Navarro Díaz', 'elena@example.com', '600666777', 'Castellón', '2026-03-08'),
('Pablo', 'Ortega Molina', 'pablo@example.com', '600777888', 'Murcia', '2026-04-03'),
('Marta', 'Vidal Castro', 'marta@example.com', '600888999', 'Bilbao', '2026-04-18'),
('Javier', 'Moreno Flores', 'javier@example.com', '600999000', 'Zaragoza', '2026-05-05'),
('Lucía', 'Herrera Ramos', 'lucia@example.com', '611000111', 'Málaga', '2026-05-20');

-- ========================================
-- 3. INSERTAR COCHES JOCARSA
-- ========================================

INSERT INTO productos
(nombre, modelo, categoria, precio, potencia, autonomia, stock)
VALUES
('JOCARSA Urban', 'U1', 'Urbano', 15900, 95, 250, 20),
('JOCARSA Urban Plus', 'U2', 'Urbano', 18900, 120, 320, 15),
('JOCARSA City', 'C1', 'Compacto', 22500, 150, 380, 12),
('JOCARSA City Sport', 'C2', 'Compacto', 27900, 210, 420, 10),
('JOCARSA Family', 'F1', 'Familiar', 32900, 180, 480, 8),
('JOCARSA Family XL', 'F2', 'Familiar', 38900, 230, 520, 6),
('JOCARSA SUV', 'S1', 'SUV', 42900, 250, 550, 10),
('JOCARSA SUV Premium', 'S2', 'SUV', 49900, 320, 600, 7),
('JOCARSA Sport', 'GT1', 'Deportivo', 59900, 420, 450, 5),
('JOCARSA Sport RS', 'GT2', 'Deportivo', 79900, 580, 500, 3),
('JOCARSA Luxury', 'L1', 'Lujo', 89900, 450, 650, 4),
('JOCARSA Luxury Executive', 'L2', 'Lujo', 119900, 650, 720, 2);

-- ========================================
-- 4. INSERTAR PEDIDOS
-- ========================================

INSERT INTO pedidos
(cliente_id, producto_id, fecha, precio_venta, estado)
VALUES
(1, 1, '2026-01-12', 15900, 'Entregado'),
(2, 3, '2026-01-20', 22500, 'Entregado'),
(3, 7, '2026-02-05', 42900, 'Entregado'),
(4, 2, '2026-02-15', 18900, 'Entregado'),
(5, 5, '2026-03-03', 32900, 'Entregado'),
(6, 8, '2026-03-12', 49900, 'Entregado'),
(7, 4, '2026-04-06', 27900, 'Entregado'),
(8, 6, '2026-04-20', 38900, 'Entregado'),
(9, 9, '2026-05-08', 59900, 'Entregado'),
(10, 10, '2026-05-22', 79900, 'Entregado'),

(1, 3, '2026-06-02', 22500, 'Entregado'),
(2, 5, '2026-06-10', 32900, 'Entregado'),
(3, 11, '2026-06-18', 89900, 'Entregado'),
(4, 1, '2026-07-01', 15900, 'Entregado'),
(5, 7, '2026-07-12', 42900, 'Entregado'),
(6, 2, '2026-07-20', 18900, 'Entregado'),
(7, 8, '2026-08-03', 49900, 'Entregado'),
(8, 4, '2026-08-15', 27900, 'Entregado'),
(9, 12, '2026-08-25', 119900, 'Entregado'),
(10, 6, '2026-09-05', 38900, 'Entregado'),

(1, 9, '2026-09-15', 59900, 'En preparación'),
(2, 7, '2026-09-22', 42900, 'En preparación'),
(3, 5, '2026-10-01', 32900, 'Pendiente'),
(4, 3, '2026-10-10', 22500, 'Pendiente'),
(5, 11, '2026-10-18', 89900, 'Pendiente');
