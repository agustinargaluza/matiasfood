-- ============================================================
-- Mati on the Way! — Script SQL
-- Proyecto: Caso 06 "Rutas Enredadas"
-- Asignatura: Sistemas de Información — UCN 2026
-- ============================================================

-- ── DDL: Creación de tablas ──────────────────────────────────

CREATE TABLE IF NOT EXISTS zonas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    descripcion TEXT,
    color_hex   TEXT DEFAULT '#22C55E'
);

CREATE TABLE IF NOT EXISTS clientes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo   TEXT NOT NULL,
    telefono          TEXT,
    direccion_defecto TEXT,
    zona_id           INTEGER REFERENCES zonas(id),
    creado_en         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS menus (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    descripcion TEXT,
    precio      INTEGER NOT NULL,
    disponible  INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS pedidos (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id        INTEGER REFERENCES clientes(id),
    menu_id           INTEGER REFERENCES menus(id),
    zona_id           INTEGER REFERENCES zonas(id),
    direccion_entrega TEXT NOT NULL,
    notas             TEXT,
    estado            TEXT DEFAULT 'pendiente'
                      CHECK(estado IN ('pendiente','en_ruta','entregado')),
    orden_ruta        INTEGER,
    precio            INTEGER DEFAULT 0,
    fecha_pedido      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega     TIMESTAMP
);

-- ── DML: Datos de prueba ─────────────────────────────────────

-- Zonas de reparto
INSERT INTO zonas (nombre, descripcion, color_hex) VALUES
    ('Zona A – Centro La Serena', 'Sector céntrico de La Serena', '#22C55E'),
    ('Zona B – Coquimbo',         'Sector Coquimbo',              '#3B82F6'),
    ('Zona C – Las Compañías',    'Sector Las Compañías',         '#8B5CF6');

-- Menús disponibles
INSERT INTO menus (nombre, descripcion, precio, disponible) VALUES
    ('Menú del día',         'Plato del día con ensalada',               5500, 1),
    ('Hamburguesa Clásica',  'Carne de res, lechuga, tomate, cheddar',   8990, 1),
    ('Hamburguesa BBQ',      'Doble carne, bacon, salsa BBQ',            8990, 1),
    ('Hamburguesa Vegana',   'Medallón de legumbres, palta, tomate',     8990, 1),
    ('Completo Italiano',    'Palta, tomate, mayonesa, mostaza',         2990, 1),
    ('Completo Vegano',      'Sin salchicha, palta, tomate, mayo vegana',2990, 1);

-- Clientes de prueba
INSERT INTO clientes (nombre_completo, telefono, direccion_defecto, zona_id) VALUES
    ('Alejandro Ramos',  '+56912340001', 'Av. Francisco de Aguirre 485, La Serena', 1),
    ('Sofía Méndez',     '+56912340002', 'Calle Balmaceda 320, La Serena',          1),
    ('Juan Torres',      '+56912340003', 'Av. del Mar 1200, La Serena',             1),
    ('Ana Castillo',     '+56912340004', 'Calle Colón 560, La Serena',              1),
    ('Diego Morales',    '+56912340005', 'Av. Cuatro Esquinas 780, La Serena',      1),
    ('Carlos Martínez',  '+56912340006', 'Av. Costanera 950, Coquimbo',             2),
    ('Pedro Soto',       '+56912340007', 'Calle Aldunate 430, Coquimbo',            2),
    ('Valentina Cruz',   '+56912340008', 'Av. Borgoño 1100, Coquimbo',              2),
    ('Marina López',     '+56912340009', 'Calle Los Aromos 234, Las Compañías',     3),
    ('Lucía Vargas',     '+56912340010', 'Pasaje Las Flores 88, Las Compañías',     3);

-- Pedidos de prueba
INSERT INTO pedidos (cliente_id, menu_id, zona_id, direccion_entrega, notas, estado, orden_ruta, precio) VALUES
    (1, 1, 1, 'Av. Francisco de Aguirre 485, La Serena', 'Sin cebolla',     'entregado', 1, 5500),
    (2, 2, 1, 'Calle Balmaceda 320, La Serena',          NULL,              'entregado', 2, 8990),
    (3, 5, 1, 'Av. del Mar 1200, La Serena',             'Extra mostaza',   'en_ruta',   3, 2990),
    (4, 3, 1, 'Calle Colón 560, La Serena',              NULL,              'pendiente', 4, 8990),
    (5, 1, 1, 'Av. Cuatro Esquinas 780, La Serena',      'Sin ensalada',    'pendiente', 5, 5500),
    (6, 2, 2, 'Av. Costanera 950, Coquimbo',             NULL,              'entregado', 6, 8990),
    (7, 4, 2, 'Calle Aldunate 430, Coquimbo',            'Extra palta',     'pendiente', 7, 8990),
    (8, 6, 2, 'Av. Borgoño 1100, Coquimbo',              NULL,              'pendiente', 8, 2990),
    (9, 1, 3, 'Calle Los Aromos 234, Las Compañías',     'Sin tomate',      'en_ruta',   9, 5500),
    (10,5, 3, 'Pasaje Las Flores 88, Las Compañías',     NULL,              'pendiente', 10,2990);

-- ── Consultas útiles de ejemplo ──────────────────────────────

-- Ver todos los pedidos de hoy con datos del cliente
-- SELECT p.id, c.nombre_completo, c.telefono, m.nombre AS menu,
--        p.direccion_entrega, p.estado, p.orden_ruta, p.precio
-- FROM pedidos p
-- JOIN clientes c ON c.id = p.cliente_id
-- JOIN menus m ON m.id = p.menu_id
-- WHERE DATE(p.fecha_pedido) = DATE('now')
-- ORDER BY p.orden_ruta;

-- Resumen del día (KPIs para el dashboard)
-- SELECT COUNT(*) AS total,
--        SUM(CASE WHEN estado='entregado' THEN 1 ELSE 0 END) AS entregados,
--        SUM(CASE WHEN estado!='entregado' THEN 1 ELSE 0 END) AS pendientes,
--        SUM(precio) AS ventas_totales
-- FROM pedidos
-- WHERE DATE(fecha_pedido) = DATE('now');

-- Clientes frecuentes ordenados por pedidos
-- SELECT c.nombre_completo, c.telefono,
--        COUNT(p.id) AS total_pedidos,
--        MAX(p.fecha_pedido) AS ultimo_pedido
-- FROM clientes c
-- LEFT JOIN pedidos p ON p.cliente_id = c.id
-- GROUP BY c.id
-- ORDER BY total_pedidos DESC;
