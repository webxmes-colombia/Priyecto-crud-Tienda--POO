# Tienda de repuestos y servicios técnicos

Proyecto académico para administrar una tienda de repuestos de computadores y registrar servicios de instalación y reparación.
La solución está organizada en frontend, API y base de datos, y se puede levantar con Docker Compose.

> **Estado actual:** el backend se conecta a MySQL, ofrece registro/inicio de sesión, autorización por permisos, catálogo, CRUD de productos y creación de pedidos. El frontend incluye ingreso, registro, catálogo, panel de productos y carrito con checkout manual. Aún faltan promociones, historial de compras y gestión administrativa de pedidos.

## Objetivo

Centralizar el inventario de repuestos y la atención de servicios técnicos. El modelo contempla productos clasificados por categoría y marca, clientes y técnicos, tipos de servicio y órdenes de trabajo con sus repuestos, costos y garantía.

## Tecnologías

- **Python 3.12 y FastAPI:** API HTTP.
- **HTML, CSS/JavaScript básico y Nginx:** página web estática.
- **MySQL 8.0:** almacenamiento relacional.
- **Docker y Docker Compose:** ejecución conjunta de los servicios.

## Estructura del proyecto

```text
.
├── backend/
│   ├── app/
│   │   ├── api/              # Endpoints HTTP
│   │   ├── core/             # Seguridad y ensamblado de dependencias
│   │   ├── domain/           # Tipos y contratos del dominio
│   │   ├── controllers/      # Espacio para controladores
│   │   ├── models/           # Espacio para modelos
│   │   ├── repositories/     # Implementaciones de persistencia
│   │   ├── routes/           # Módulos de rutas existentes
│   │   ├── services/         # Casos de uso y lógica de negocio
│   │   └── main.py           # Aplicación FastAPI y ruta de salud
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html            # Acceso, catálogo y panel administrativo
│   ├── styles.css            # Estilos adaptables
│   ├── assets/
│   │   └── logo.svg           # Logo vectorial de la tienda
│   └── js/
│       ├── api.js            # Cliente HTTP y token de sesión
│       ├── auth.js           # Registro, ingreso y salida
│       ├── catalog.js        # Catálogo público y filtros
│       ├── cart.js           # Carrito local y checkout
│       ├── admin.js          # Dashboard e inventario
│       └── app.js            # Inicialización de la interfaz
│   └── Dockerfile
├── migrations/
│   └── 002_comercio.sql      # Roles, cuentas, promociones y pedidos
├── tienda_repuestos.sql      # Esquema y datos de ejemplo
└── docker-compose.yml        # Servicios frontend, backend y MySQL
```

## Arquitectura

Docker Compose inicia tres servicios:

1. **Frontend** en `http://localhost:8080`, servido por Nginx. Incluye ingreso, registro, catálogo y administración inicial.
2. **Backend** en `http://localhost:8000`, construido con FastAPI. También está disponible su documentación interactiva en `http://localhost:8000/docs`.
3. **Base de datos** MySQL 8.0 en el puerto `3306`, con la base `tienda_repuestos`.
4. **phpMyAdmin** en `http://localhost:8081`, para administrar MySQL desde el navegador.

### Identidad visual

El frontend utiliza el logo vectorial `frontend/assets/logo.svg`, seleccionado de los archivos existentes de la marca. La paleta parte de los colores del logo: azul marino `#04152B`, azul `#4DA5C4`, naranja `#E27D2C` y verde `#72AE46`. Los botones y textos usan tonos oscuros para mantener contraste; el naranja y el azul claro quedan como acentos.

### Dominio de producción

El dominio previsto es `https://repuestoscomputadorbogota.com`. El frontend lo declara como URL canónica y usa el mismo origen para la API cuando se sirve desde un dominio público. En local continúa llamando a `http://localhost:8000`; se puede sobrescribir la dirección de API con `window.TIENDA_API_URL`.

Para publicar el sitio faltan configurar los registros DNS hacia el servidor, HTTPS y un proxy inverso que envíe `/` al frontend y `/api` al backend. La base MySQL debe permanecer accesible solo para los servicios del servidor, no para visitantes.

El navegador llama a `http://localhost:8000/api/health`. Entre contenedores, el backend se conecta a MySQL usando el nombre de servicio `db` (no `localhost`). La ruta realiza una consulta `SELECT 1`; si MySQL no está disponible, responde con estado HTTP 503. Compose espera a que el chequeo de MySQL esté saludable antes de iniciar el backend.

### Autenticación disponible

- `POST /api/auth/register`: crea una cuenta de cliente vinculada a `clientes` y devuelve un token de acceso.
- `POST /api/auth/login`: valida correo y contraseña y devuelve un token.
- `GET /api/auth/me`: requiere `Authorization: Bearer <token>` y devuelve la cuenta autenticada.

El registro solicita nombre, correo, contraseña, teléfono y dirección. Siempre asigna el rol `cliente`; el cliente no puede elegir roles internos. Las contraseñas se guardan como hash scrypt. El token JWT usa PyJWT y el algoritmo HS256, con algoritmo de verificación fijado explícitamente según la guía oficial de [PyJWT](https://pyjwt.readthedocs.io/en/stable/). En desarrollo Compose define una clave de demostración; antes de desplegar, configura una `JWT_SECRET_KEY` privada de al menos 32 caracteres.

### Autorización y dashboard inicial

- `GET /api/admin/dashboard/summary` devuelve conteos de productos, existencias bajas, clientes, pedidos pendientes y promociones activas.
- Requiere un token válido y el permiso `usuarios.gestionar`, asignado a administrador y superusuario. El permiso se consulta en MySQL en cada solicitud.
- El registro público solo crea clientes. La primera cuenta privilegiada se crea manualmente con el comando protegido descrito abajo.

Para crear el primer superusuario con Docker en ejecución, ejecuta desde la raíz del proyecto:

```bash
docker compose exec backend python -m app.commands.create_superuser
```

El comando solicita correo y contraseña de forma interactiva; la contraseña no se muestra en pantalla, debe tener al menos 12 caracteres y confirmarse. Solo permite crear el primer superusuario y no agrega credenciales fijas al proyecto. Después podrás iniciar sesión en `/api/auth/login` y usar el token para consultar el dashboard.

### Catálogo y productos

- `GET /api/catalog/products`: catálogo público de productos activos; acepta `search`, `category_id`, `brand_id`, `limit` y `offset`.
- `GET /api/catalog/categories` y `GET /api/catalog/brands`: opciones para filtros y formularios.
- `POST /api/admin/brands`: crea una marca; requiere `productos.gestionar` y responde con conflicto si el nombre ya existe.
- `GET /api/admin/products`: lista productos para administración; `include_inactive=true` incluye los desactivados.
- `POST /api/admin/products`: crea un producto.
- `PUT /api/admin/products/{product_id}`: actualiza sus datos.
- `DELETE /api/admin/products/{product_id}`: lo desactiva lógicamente para conservar su referencia histórica.

Las rutas administrativas de productos y marcas requieren `productos.gestionar`, asignado a vendedor, administrador y superusuario. Los precios y el stock se validan en el servidor; no se permite precio negativo ni stock negativo. El panel permite crear, editar, desactivar y reactivar productos, además de crear marcas. El token se mantiene en `sessionStorage` durante la sesión actual del navegador.

### Carrito y pedidos

- El carrito se guarda en `localStorage`, por lo que sobrevive a recargar la página en el mismo navegador. Permite agregar productos, ajustar cantidades y retirarlos.
- Para confirmar, el cliente inicia sesión o crea una cuenta y confirma correo, teléfono y dirección de entrega.
- `POST /api/orders` requiere `pedidos.crear`. Acepta contraentrega, Nequi o Daviplata; los pagos manuales quedan pendientes y no se realiza cobro en línea.
- El servidor consulta los precios y existencias en MySQL, no confía en los valores guardados en el navegador, y crea el pedido con sus detalles y la disminución de stock en una sola transacción. Si un producto está agotado o no hay suficiente stock, cancela toda la operación.
- El total actual incluye los productos. El costo de entrega se coordina aparte y se confirma con la tienda. Las promociones aún no se descuentan del total.

## Principios SOLID

SOLID guía la implementación de los módulos de negocio. Los principios están aplicados en autenticación, autorización, dashboard, catálogo y pedidos; promociones e historial se incorporarán en las siguientes etapas.

| Principio | Aplicación prevista en esta tienda | Cuándo se aplicará |
|---|---|---|
| **S — Responsabilidad única** | Las rutas validan HTTP, servicios aplican reglas, repositorios consultan MySQL; en el frontend cada módulo gestiona una función concreta. | **Aplicado en autenticación, dashboard, catálogo y pedidos:** cada capa tiene un módulo específico; el frontend separa API, sesión, catálogo, carrito y administración, incluyendo el alta de marcas. |
| **O — Abierto/cerrado** | Añadir un nuevo tipo de descuento o método manual de pago mediante una implementación nueva, evitando modificar el flujo central de pedidos. | Al desarrollar promociones y pagos; cambios pequeños se revisarán antes de extender el diseño. |
| **L — Sustitución de Liskov** | Una implementación concreta de una abstracción debe poder reemplazar a otra respetando el contrato. Por ejemplo, las políticas de descuento deben aceptar los mismos datos y devolver un descuento válido dentro del subtotal. | Al crear y revisar las políticas de descuento porcentual y de valor fijo. |
| **I — Segregación de interfaces** | Usar contratos pequeños y específicos para que cada servicio reciba solo las operaciones que necesita. | **Aplicado:** `AuthRepository`, `AuthorizationRepository`, `DashboardRepository`, `SuperuserBootstrapRepository`, `CatalogRepository` y `OrderRepository` están separados. |
| **D — Inversión de dependencias** | Los servicios dependen de abstracciones; FastAPI conecta implementaciones concretas mediante inyección de dependencias. | **Aplicado en autenticación, autorización, dashboard, catálogo y pedidos:** cada servicio recibe su contrato; `core/dependencies.py` conecta MySQL. En frontend, las vistas reciben el cliente `StoreApi`. |

**ISP aplicado:** los contratos separados evitan que cada módulo dependa de operaciones que no usa. **OCP y LSP quedan planificados para promociones:** aún no existen implementaciones de descuentos en el backend; se documentarán como aplicados cuando se construyan y respeten sus contratos.

La interfaz usa clases pequeñas (`StoreApi`, `AuthController`, `CatalogController` y `AdminController`) para encapsular estado y comportamiento del frontend. La composición en `app.js` las conecta; no se usa herencia artificial.

**Nota de alcance SOLID:** el repositorio convierte el error de índice único de MySQL en un error del dominio (`AccountAlreadyExists`); el servicio no necesita conocer PyMySQL. La composición concreta ocurre en `core/dependencies.py`, donde FastAPI conecta el servicio con el repositorio MySQL.

### Estructura objetivo del backend

```text
backend/app/
├── api/             # Rutas HTTP y esquemas de entrada/salida
├── domain/          # Entidades, contratos y reglas de negocio
├── services/        # Casos de uso: login, catálogo, promociones y pedidos
├── repositories/    # Implementaciones de acceso a MySQL
└── core/            # Configuración, seguridad y dependencias compartidas
```

Esta estructura es una guía; se ajustará si una separación añade archivos sin aislar una responsabilidad real. La herencia no se usará como requisito automático: para descuentos y pagos se preferirá una abstracción pequeña y composición, con herencia solo si las implementaciones comparten un contrato estable.

## Modelo de datos

El script `tienda_repuestos.sql` crea ocho tablas de inventario y servicios:

| Tabla | Propósito y relaciones principales |
|---|---|
| `categorias` | Clasifica los productos. |
| `marcas` | Registra marcas y país de origen. |
| `productos` | Repuestos con precio, stock, categoría, marca y estado. |
| `clientes` | Datos de contacto de los clientes. |
| `tecnicos` | Técnicos, especialidad y disponibilidad. |
| `tipos_servicio` | Catálogo de servicios y valor de mano de obra. |
| `ordenes_servicio` | Equipo recibido, cliente, técnico, fechas y estado. |
| `detalle_orden_servicio` | Productos y servicios incluidos en cada orden, cantidades, precios y garantía. |

Las relaciones se implementan con claves foráneas. También hay restricciones para evitar precios o cantidades negativos y para limitar los estados de una orden: `recibido`, `en_proceso`, `pendiente_repuesto`, `terminado`, `entregado` y `cancelado`.

El script inserta datos de demostración: cinco categorías, marcas, productos, clientes, técnicos, tipos de servicio, órdenes y detalles. Al final incluye una consulta que une la orden con el cliente, técnico, repuesto y servicio para mostrar el costo del detalle.

La migración `migrations/002_comercio.sql` agrega las tablas `roles`, `permisos`, `rol_permisos`, `usuarios`, `promociones`, `promocion_productos`, `pedidos` y `detalle_pedidos`. Conserva el esquema de servicios técnicos. El carrito se guardará en el navegador en la primera versión; al confirmar la compra, el backend deberá validar nuevamente precios, promociones y existencias antes de guardar el pedido.

Los cuatro roles iniciales son `cliente`, `vendedor`, `administrador` y `superusuario`. El registro público deberá asignar solo el rol cliente. Las cuentas internas se crearán de manera controlada y los permisos se validarán en el backend.

## Requisitos

- Docker Desktop instalado y en ejecución.
- Docker Compose (incluido en versiones actuales de Docker Desktop).
- Puertos locales `3306`, `8000` y `8080` disponibles.

No es necesario instalar Python o MySQL localmente: los contenedores usan las imágenes descritas en sus Dockerfiles y en Compose.

## Cómo iniciar

Desde la carpeta raíz del proyecto, ejecuta:

```bash
docker compose up --build
```

Cuando finalice la construcción, abre:

- Aplicación web: [http://localhost:8080](http://localhost:8080)
- Comprobación de API: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Documentación interactiva de FastAPI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Administrador visual de MySQL: [http://localhost:8081](http://localhost:8081) (servidor `db`, usuario `root`, contraseña `root`).

La API debe responder con:

```json
  {"estado":"Backend y base de datos funcionando","base_de_datos":"conectada"}
```

La página web muestra el mismo mensaje si pudo comunicarse con la API.

Para detener los contenedores, usa `Ctrl+C` y luego:

```bash
docker compose down
```

Para detenerlos y borrar también los datos persistidos de MySQL (incluidos los datos de ejemplo), usa:

```bash
docker compose down -v
```

## Inicialización de MySQL

Compose monta `tienda_repuestos.sql` y `migrations/002_comercio.sql` en la carpeta de inicialización de MySQL. MySQL ejecuta ambos en orden al crear por primera vez el directorio de datos. Compose conserva los datos en el volumen `mysql_data`, por lo que los scripts no se aplican automáticamente a una base ya inicializada. La migración debe ejecutarse de forma controlada sobre una base existente; eliminar el volumen con `docker compose down -v` borra permanentemente todos los datos guardados en él.

La configuración de desarrollo define `MYSQL_ROOT_PASSWORD=root`. Cambia esa credencial antes de cualquier uso fuera de un entorno local de demostración.

## Archivos principales

- `docker-compose.yml`: puertos, dependencias, montaje del SQL y volumen persistente de MySQL.
- `backend/app/main.py`: instancia FastAPI, configuración CORS y endpoint `GET /api/health`.
- `backend/app/database.py`: crea conexiones a MySQL con los parámetros de entorno `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`.
- `backend/app/api/auth.py`: endpoints de registro, inicio de sesión y consulta de cuenta.
- `backend/app/api/admin.py`: resumen administrativo protegido por permiso.
- `backend/app/api/catalog.py`: catálogo público y CRUD administrativo de productos.
- `backend/app/api/brands.py`: creación administrativa de marcas protegida por permiso.
- `backend/app/api/orders.py`: checkout que valida al comprador, el método manual de pago y los datos de entrega.
- `backend/app/commands/create_superuser.py`: comando interactivo para la cuenta privilegiada inicial.
- `backend/app/services/auth_service.py`: reglas del caso de uso de autenticación.
- `backend/app/services/authorization_service.py`: decisión de permisos.
- `backend/app/services/dashboard_service.py`: caso de uso del resumen administrativo.
- `backend/app/services/catalog_service.py`: reglas del catálogo y normalización de datos de producto.
- `backend/app/services/order_service.py`: normaliza artículos repetidos y valida límites del pedido.
- `backend/app/services/superuser_bootstrap_service.py`: valida la creación del superusuario inicial.
- `backend/app/repositories/auth_repository.py`: transacciones y consultas MySQL para cuentas.
- `backend/app/repositories/authorization_repository.py`: consulta permisos efectivos por cuenta.
- `backend/app/repositories/dashboard_repository.py`: conteos agregados del dashboard.
- `backend/app/repositories/catalog_repository.py`: consultas del catálogo, categorías, marcas y productos.
- `backend/app/repositories/order_repository.py`: transacción de pedido, detalle y descuento de stock.
- `backend/app/repositories/superuser_bootstrap_repository.py`: crea la cuenta inicial en una transacción.
- `backend/app/core/access_control.py`: dependencia que bloquea solicitudes sin permiso.
- `backend/app/core/security.py`: hash scrypt de contraseñas y emisión/validación de tokens JWT.
- `backend/app/domain/repositories.py`: contrato específico de persistencia para autenticación.
- `frontend/js/api.js`: cliente HTTP que agrega token y traduce errores de API.
- `frontend/js/auth.js`: controla ingreso, registro, restauración de sesión y salida.
- `frontend/js/catalog.js`: filtros y tarjetas del catálogo público.
- `frontend/js/cart.js`: carrito local, datos de entrega y confirmación de pedido.
- `frontend/js/admin.js`: resumen, formulario y tabla de productos.
- `frontend/js/app.js`: composición e inicialización de la interfaz.
- `frontend/styles.css`: presentación adaptable para móvil y escritorio.
- `frontend/assets/logo.svg`: logo vectorial de la marca.
- `backend/requirements.txt`: dependencias Python (`fastapi`, `uvicorn[standard]`, `PyMySQL` y `PyJWT`).
- `frontend/index.html`: página mínima que consulta el endpoint de salud.
- `tienda_repuestos.sql`: creación de tablas, relaciones y registros de muestra.
- `migrations/002_comercio.sql`: tablas iniciales de seguridad, promociones y pedidos.

## Guion breve para la exposición

1. **Presentación:** “Este proyecto propone una solución para una tienda de repuestos de computadores que también presta servicios técnicos. Busca organizar el inventario y el seguimiento de las reparaciones.”
2. **Necesidad:** “La información de productos, clientes, técnicos y trabajos de servicio debe estar relacionada y ser fácil de consultar.”
3. **Diseño:** explicar la separación en frontend, backend y base de datos; mostrar las ocho tablas y las relaciones entre órdenes, clientes, técnicos, repuestos y servicios.
4. **Demostración actual:** iniciar la aplicación, abrir `localhost:8080` y mostrar la comprobación de conectividad. Después, abrir `/docs` y `/api/health`.
5. **Cierre y trabajo pendiente:** “La base de datos ya tiene un modelo y datos de ejemplo. La siguiente etapa es conectar FastAPI con MySQL e implementar las operaciones CRUD y las pantallas de gestión.”

## Alcance implementado y próximos pasos

**Implementado:** contenedores para la página, API, MySQL y phpMyAdmin; esquema de servicios, roles, permisos, promociones y pedidos; conexión del backend a MySQL; registro e inicio de sesión con contraseña protegida y token; autorización por permisos; resumen administrativo; catálogo, CRUD protegido de productos y alta protegida de marcas; carrito local y creación transaccional de pedidos con pago manual; interfaz web inicial para esas funciones.

**Pendiente:** recuperación de contraseña, promociones y cupones, historial de compras, administración y confirmación de pedidos/pagos, configuración del costo de envío y pruebas.

Una secuencia práctica para continuar sería implementar primero la conexión y el CRUD de categorías y productos, luego clientes y técnicos, y finalmente órdenes de servicio y sus detalles.
