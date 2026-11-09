-- Base de datos para una tienda de repuestos y servicios de instalación.
-- Ejecutar en MySQL 8.0 o superior.

CREATE DATABASE IF NOT EXISTS tienda_repuestos
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE tienda_repuestos;

CREATE TABLE IF NOT EXISTS categorias (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS marcas (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    pais_origen VARCHAR(80),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS productos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(160) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(12, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    categoria_id INT UNSIGNED NOT NULL,
    marca_id INT UNSIGNED NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_producto_precio CHECK (precio >= 0),
    CONSTRAINT chk_producto_stock CHECK (stock >= 0),
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    CONSTRAINT fk_producto_marca
        FOREIGN KEY (marca_id) REFERENCES marcas(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clientes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(150) UNIQUE,
    telefono VARCHAR(30),
    direccion VARCHAR(200),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tecnicos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(30),
    especialidad VARCHAR(120),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipos_servicio (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NOT NULL,
    precio_mano_obra DECIMAL(12, 2) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_servicio_precio CHECK (precio_mano_obra >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ordenes_servicio (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT UNSIGNED NOT NULL,
    tecnico_id INT UNSIGNED NULL,
    fecha_recepcion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega DATETIME NULL,
    estado ENUM('recibido', 'en_proceso', 'pendiente_repuesto', 'terminado', 'entregado', 'cancelado')
        NOT NULL DEFAULT 'recibido',
    equipo_tipo VARCHAR(80) NOT NULL,
    equipo_marca VARCHAR(80) NOT NULL,
    equipo_modelo VARCHAR(100) NOT NULL,
    numero_serie VARCHAR(100),
    observaciones TEXT,
    CONSTRAINT fk_orden_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_orden_tecnico
        FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_orden_servicio (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    orden_servicio_id INT UNSIGNED NOT NULL,
    tipo_servicio_id INT UNSIGNED NOT NULL,
    producto_id INT UNSIGNED NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_repuesto DECIMAL(12, 2) NOT NULL,
    precio_mano_obra DECIMAL(12, 2) NOT NULL,
    garantia_dias INT NOT NULL DEFAULT 30,
    CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_garantia CHECK (garantia_dias >= 0),
    CONSTRAINT fk_detalle_orden
        FOREIGN KEY (orden_servicio_id) REFERENCES ordenes_servicio(id),
    CONSTRAINT fk_detalle_tipo_servicio
        FOREIGN KEY (tipo_servicio_id) REFERENCES tipos_servicio(id),
    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (producto_id) REFERENCES productos(id)
) ENGINE=InnoDB;

-- Cinco categorías.
INSERT INTO categorias (nombre, descripcion) VALUES
('Pantallas', 'Pantallas para portatiles y computadores todo en uno'),
('Teclados', 'Teclados para portatiles y equipos de escritorio'),
('Baterias', 'Baterias internas y externas para portatiles'),
('Almacenamiento', 'Discos duros y unidades de estado solido'),
('Memorias RAM', 'Módulos de memoria RAM para computadores');

-- Cinco marcas.
INSERT INTO marcas (nombre, pais_origen) VALUES
('Kingston', 'Estados Unidos'),
('Crucial', 'Estados Unidos'),
('Seagate', 'Estados Unidos'),
('HP', 'Estados Unidos'),
('Lenovo', 'China'),
('OEM', 'No aplica'),
('Adata', 'Estados Unidos'),
('Samsung', 'Corea del Sur'),
('Western Digital', 'Estados Unidos');


-- Cinco productos. Sus identificadores se usarán en los servicios.
INSERT INTO productos (nombre, descripcion, precio, stock, categoria_id, marca_id) VALUES
('Pantalla LED 15.6 pulgadas HD', 'Pantalla compatible con portatiles HP de 15.6 pulgadas', 280000.00, 8, 1, 4),
('Teclado para portátil Lenovo IdeaPad', 'Teclado español compatible con Lenovo IdeaPad 3', 120000.00, 12, 2, 5),
('Bateria para HP Pavilion', 'Bateria interna compatible con HP Pavilion 15', 180000.00, 6, 3, 4),
('Disco SSD Kingston NV3 1 TB', 'Unidad SSD NVMe M.2 de 1 TB', 350000.00, 10, 4, 1),
('Memoria RAM Crucial 16 GB DDR4', 'Memoria DDR4 SODIMM de 16 GB para portatil', 220000.00, 15, 5, 2);

-- Cinco clientes.
INSERT INTO clientes (nombre, correo, telefono, direccion) VALUES
('Adriana Gomez', 'ana.gomez@example.com', '3001112233', 'Calle 10 # 20-30'),
('Cesar Martinez', 'cesar.martinez@example.com', '3002223344', 'Carrera 15 # 30-45'),
('Valeria Rodriguez', 'valeria.rodriguez@example.com', '3003334455', 'Calle 25 # 18-12'),
('Emily Martinez', 'emily.martinez@example.com', '3004445566', 'Avenida 6 # 40-20'),
('Carmen Torres', 'carmen.torres@example.com', '3005556677', 'Calle 40 # 12-08');

-- Cinco técnicos.
INSERT INTO tecnicos (nombre, telefono, especialidad) VALUES
('Diego Ramirez', '3101112233', 'Pantallas y carcasas'),
('Leona Torres', '3102223344', 'Almacenamiento y sistemas operativos'),
('Miguel Castro', '3103334455', 'Memoria RAM y mantenimiento'),
('Paola Herrera', '3104445566', 'Teclados y baterías'),
('Jorge Salazar', '3105556677', 'Diagnóstico de portátiles');

-- Cinco tipos de servicio técnico.
INSERT INTO tipos_servicio (nombre, descripcion, precio_mano_obra) VALUES
('Instalacion de pantalla', 'Desmontaje, instalacion y prueba de pantalla nueva', 80000.00),
('Instalacion de teclado', 'Reemplazo y prueba del teclado del portatil', 50000.00),
('Cambio de batería', 'Instalación y prueba de batería compatible', 40000.00),
('Instalacion de disco SSD', 'Instalación física y verificacion de la unidad', 45000.00),
('Instalacion de memoria RAM', 'Instalacion y prueba de memoria RAM', 30000.00);

-- Cinco órdenes de servicio.
INSERT INTO ordenes_servicio
    (cliente_id, tecnico_id, fecha_recepcion, fecha_entrega, estado, equipo_tipo, equipo_marca, equipo_modelo, numero_serie, observaciones)
VALUES
    (1, 1, '2026-10-20 09:00:00', NULL, 'en_proceso', 'Portátil', 'HP', 'Pavilion 15', 'HP-PAV-001', 'Pantalla rota por golpe.'),
    (2, 4, '2026-10-20 10:30:00', NULL, 'en_proceso', 'Portátil', 'Lenovo', 'IdeaPad 3', 'LEN-IDE-002', 'Varias teclas no responden.'),
    (3, 4, '2026-10-21 08:15:00', NULL, 'pendiente_repuesto', 'Portátil', 'HP', 'Pavilion 15', 'HP-PAV-003', 'La batería no conserva carga.'),
    (4, 2, '2026-10-21 14:00:00', '2026-10-22 16:00:00', 'terminado', 'Portátil', 'Lenovo', 'ThinkBook 14', 'LEN-THI-004', 'Se instaló SSD y se verificó su funcionamiento.'),
    (5, 3, '2026-10-22 11:00:00', NULL, 'recibido', 'Portátil', 'HP', 'ProBook 440', 'HP-PRO-005', 'Equipo lento; se solicita ampliación de RAM.');

-- Cinco detalles: un producto instalado por cada orden de servicio.
INSERT INTO detalle_orden_servicio
    (orden_servicio_id, tipo_servicio_id, producto_id, cantidad, precio_repuesto, precio_mano_obra, garantia_dias)
VALUES
    (1, 1, 1, 1, 280000.00, 80000.00, 90),
    (2, 2, 2, 1, 120000.00, 50000.00, 60),
    (3, 3, 3, 1, 180000.00, 40000.00, 90),
    (4, 4, 4, 1, 350000.00, 45000.00, 90),
    (5, 5, 5, 1, 220000.00, 30000.00, 60);

-- Consulta para revisar cada orden, sus costos y el total.
SELECT
    os.id AS orden_servicio,
    c.nombre AS cliente,
    t.nombre AS tecnico,
    os.estado,
    p.nombre AS repuesto_instalado,
    ts.nombre AS servicio,
    dos.precio_repuesto,
    dos.precio_mano_obra,
    (dos.cantidad * dos.precio_repuesto) + dos.precio_mano_obra AS total_detalle
FROM ordenes_servicio AS os
INNER JOIN clientes AS c ON c.id = os.cliente_id
LEFT JOIN tecnicos AS t ON t.id = os.tecnico_id
INNER JOIN detalle_orden_servicio AS dos ON dos.orden_servicio_id = os.id
INNER JOIN productos AS p ON p.id = dos.producto_id
INNER JOIN tipos_servicio AS ts ON ts.id = dos.tipo_servicio_id
ORDER BY os.id;

CREATE TABLE IF NOT EXISTS roles (
    id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(40) NOT NULL UNIQUE,
    descripcion VARCHAR(180),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS permisos (
    id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(180) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rol_permisos (
    rol_id SMALLINT UNSIGNED NOT NULL,
    permiso_id SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (rol_id, permiso_id),
    CONSTRAINT fk_rol_permisos_rol
        FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_rol_permisos_permiso
        FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Una cuenta de cliente se vincula a clientes. Las cuentas internas pueden
-- tener cliente_id NULL. El registro público solo asignará el rol cliente.
CREATE TABLE IF NOT EXISTS usuarios (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT UNSIGNED NULL UNIQUE,
    rol_id SMALLINT UNSIGNED NOT NULL,
    nombre VARCHAR(120) NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    CONSTRAINT fk_usuario_rol
        FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS promociones (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    descripcion VARCHAR(255),
    modalidad ENUM('automatica', 'cupon') NOT NULL,
    codigo VARCHAR(40) NULL UNIQUE,
    tipo_descuento ENUM('porcentaje', 'valor_fijo') NOT NULL,
    valor DECIMAL(12, 2) NOT NULL,
    compra_minima DECIMAL(12, 2) NOT NULL DEFAULT 0,
    empieza_en DATETIME NOT NULL,
    termina_en DATETIME NOT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_promocion_valor CHECK (valor > 0),
    CONSTRAINT chk_promocion_minimo CHECK (compra_minima >= 0),
    CONSTRAINT chk_promocion_porcentaje CHECK (tipo_descuento <> 'porcentaje' OR valor <= 100),
    CONSTRAINT chk_promocion_fechas CHECK (termina_en > empieza_en),
    CONSTRAINT chk_promocion_codigo CHECK (
        (modalidad = 'cupon' AND codigo IS NOT NULL) OR
        (modalidad = 'automatica' AND codigo IS NULL)
    )
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS promocion_productos (
    promocion_id INT UNSIGNED NOT NULL,
    producto_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (promocion_id, producto_id),
    CONSTRAINT fk_promocion_productos_promocion
        FOREIGN KEY (promocion_id) REFERENCES promociones(id) ON DELETE CASCADE,
    CONSTRAINT fk_promocion_productos_producto
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pedidos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT UNSIGNED NOT NULL,
    promocion_id INT UNSIGNED NULL,
    promocion_nombre VARCHAR(120) NULL,
    codigo_cupon VARCHAR(40) NULL,
    correo_entrega VARCHAR(150) NOT NULL,
    telefono_entrega VARCHAR(30) NOT NULL,
    direccion_entrega VARCHAR(200) NOT NULL,
    metodo_pago ENUM('contraentrega', 'nequi', 'daviplata') NOT NULL,
    estado_pago ENUM('pendiente', 'confirmado', 'rechazado') NOT NULL DEFAULT 'pendiente',
    estado ENUM('recibido', 'confirmado', 'preparando', 'enviado', 'entregado', 'cancelado')
        NOT NULL DEFAULT 'recibido',
    subtotal DECIMAL(12, 2) NOT NULL,
    descuento DECIMAL(12, 2) NOT NULL DEFAULT 0,
    costo_envio DECIMAL(12, 2) NOT NULL DEFAULT 0,
    total DECIMAL(12, 2) NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    CONSTRAINT fk_pedido_promocion
        FOREIGN KEY (promocion_id) REFERENCES promociones(id) ON DELETE SET NULL,
    CONSTRAINT chk_pedido_subtotal CHECK (subtotal >= 0),
    CONSTRAINT chk_pedido_descuento CHECK (descuento >= 0),
    CONSTRAINT chk_pedido_envio CHECK (costo_envio >= 0),
    CONSTRAINT chk_pedido_total CHECK (total >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_pedidos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT UNSIGNED NOT NULL,
    producto_id INT UNSIGNED NOT NULL,
    producto_nombre VARCHAR(160) NOT NULL,
    precio_unitario DECIMAL(12, 2) NOT NULL,
    cantidad INT UNSIGNED NOT NULL,
    subtotal_linea DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_detalle_pedido
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_pedido_producto
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT,
    CONSTRAINT chk_detalle_pedido_precio CHECK (precio_unitario >= 0),
    CONSTRAINT chk_detalle_pedido_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_pedido_subtotal CHECK (subtotal_linea >= 0)
) ENGINE=InnoDB;

INSERT IGNORE INTO roles (nombre, descripcion) VALUES
    ('cliente', 'Compra productos y consulta sus propios pedidos'),
    ('vendedor', 'Gestiona productos, existencias y pedidos'),
    ('administrador', 'Administra promociones, cuentas y la tienda'),
    ('superusuario', 'Acceso total y configuración del sistema');

INSERT IGNORE INTO permisos (codigo, descripcion) VALUES
    ('catalogo.leer', 'Consultar catálogo y promociones'),
    ('pedidos.crear', 'Crear pedidos'),
    ('pedidos.leer_propios', 'Consultar pedidos propios'),
    ('pedidos.gestionar', 'Consultar y actualizar pedidos de clientes'),
    ('productos.gestionar', 'Crear, editar y desactivar productos'),
    ('inventario.gestionar', 'Actualizar existencias'),
    ('promociones.gestionar', 'Crear y administrar promociones y cupones'),
    ('usuarios.gestionar', 'Crear y administrar cuentas internas y clientes'),
    ('roles.gestionar', 'Asignar roles y administrar permisos'),
    ('sistema.gestionar', 'Administrar la configuración global del sistema');

INSERT IGNORE INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permisos p
WHERE r.nombre = 'cliente'
  AND p.codigo IN ('catalogo.leer', 'pedidos.crear', 'pedidos.leer_propios');

INSERT IGNORE INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permisos p
WHERE r.nombre = 'vendedor'
  AND p.codigo IN ('catalogo.leer', 'pedidos.crear', 'pedidos.gestionar', 'productos.gestionar', 'inventario.gestionar');

INSERT IGNORE INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permisos p
WHERE r.nombre = 'administrador'
  AND p.codigo IN ('catalogo.leer', 'pedidos.crear', 'pedidos.leer_propios', 'pedidos.gestionar', 'productos.gestionar', 'inventario.gestionar', 'promociones.gestionar', 'usuarios.gestionar', 'roles.gestionar');

INSERT IGNORE INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permisos p
WHERE r.nombre = 'superusuario';

-- Cuenta administrativa inicial. El hash usa el formato scrypt de Werkzeug.
INSERT INTO usuarios (nombre, correo, password_hash, rol_id, activo)
SELECT 'Cesar A Martinez', 'admin@empresa.com',
       'scrypt:32768:8:1$C5TOPxqNXD5rGbIL$443bb11d941697e17337af318c6acfb97c519719a5fd5d5203e2203c6e549745cdd08945dff0da7d6bcc96cbee084cba80800facb3489f259d3ca02162923428',
       r.id, TRUE
FROM roles AS r
WHERE r.nombre = 'superusuario'
  AND NOT EXISTS (SELECT 1 FROM usuarios WHERE correo = 'admin@empresa.com');

