"""Persistencia MySQL para catálogo y productos."""

from collections.abc import Callable
from decimal import Decimal

import pymysql
from pymysql.connections import Connection

from app.domain.catalog import BrandDraft, CatalogOption, Product, ProductDraft
from app.domain.errors import BrandAlreadyExists, InvalidProductReference, ProductNotFound


class MySQLCatalogRepository:
    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    @staticmethod
    def _to_product(row: dict) -> Product:
        return Product(
            id=int(row["id"]),
            name=row["nombre"],
            description=row["descripcion"],
            price=Decimal(row["precio"]),
            stock=int(row["stock"]),
            category_id=int(row["categoria_id"]),
            category_name=row["categoria_nombre"],
            brand_id=int(row["marca_id"]),
            brand_name=row["marca_nombre"],
            active=bool(row["activo"]),
            created_at=row["creado_en"],
        )

    @staticmethod
    def _select_product(cursor, product_id: int) -> Product | None:
        cursor.execute(
            """SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock,
                      p.categoria_id, c.nombre AS categoria_nombre,
                      p.marca_id, m.nombre AS marca_nombre, p.activo, p.creado_en
               FROM productos AS p
               INNER JOIN categorias AS c ON c.id = p.categoria_id
               INNER JOIN marcas AS m ON m.id = p.marca_id
               WHERE p.id = %s LIMIT 1""",
            (product_id,),
        )
        row = cursor.fetchone()
        return MySQLCatalogRepository._to_product(row) if row else None

    def list_products(self, *, include_inactive: bool, category_id: int | None, brand_id: int | None,
                      search: str | None, limit: int, offset: int) -> list[Product]:
        conditions: list[str] = []
        parameters: list[object] = []
        if not include_inactive:
            conditions.append("p.activo = TRUE")
        if category_id is not None:
            conditions.append("p.categoria_id = %s")
            parameters.append(category_id)
        if brand_id is not None:
            conditions.append("p.marca_id = %s")
            parameters.append(brand_id)
        if search:
            conditions.append("(p.nombre LIKE %s OR p.descripcion LIKE %s)")
            pattern = f"%{search.strip()}%"
            parameters.extend((pattern, pattern))
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        parameters.extend((limit, offset))

        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock,
                               p.categoria_id, c.nombre AS categoria_nombre,
                               p.marca_id, m.nombre AS marca_nombre, p.activo, p.creado_en
                        FROM productos AS p
                        INNER JOIN categorias AS c ON c.id = p.categoria_id
                        INNER JOIN marcas AS m ON m.id = p.marca_id
                        {where_clause}
                        ORDER BY p.nombre ASC LIMIT %s OFFSET %s""",
                    tuple(parameters),
                )
                return [self._to_product(row) for row in cursor.fetchall()]
        finally:
            connection.close()

    def get_product(self, product_id: int) -> Product | None:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                return self._select_product(cursor, product_id)
        finally:
            connection.close()

    @staticmethod
    def _draft_values(draft: ProductDraft) -> tuple[object, ...]:
        return (draft.name, draft.description, draft.price, draft.stock, draft.category_id, draft.brand_id)

    def create_product(self, draft: ProductDraft) -> Product:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO productos
                       (nombre, descripcion, precio, stock, categoria_id, marca_id)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    self._draft_values(draft),
                )
                product_id = int(cursor.lastrowid)
            connection.commit()
        except pymysql.err.IntegrityError as error:
            connection.rollback()
            if error.args and error.args[0] == 1452:
                raise InvalidProductReference from error
            raise
        finally:
            connection.close()
        product = self.get_product(product_id)
        if product is None:
            raise RuntimeError("No se pudo recuperar el producto creado.")
        return product

    def update_product(self, product_id: int, draft: ProductDraft) -> Product:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                if self._select_product(cursor, product_id) is None:
                    raise ProductNotFound
                cursor.execute(
                    """UPDATE productos
                       SET nombre = %s, descripcion = %s, precio = %s, stock = %s,
                           categoria_id = %s, marca_id = %s
                       WHERE id = %s""",
                    (*self._draft_values(draft), product_id),
                )
            connection.commit()
        except pymysql.err.IntegrityError as error:
            connection.rollback()
            if error.args and error.args[0] == 1452:
                raise InvalidProductReference from error
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        product = self.get_product(product_id)
        if product is None:
            raise ProductNotFound
        return product

    def deactivate_product(self, product_id: int) -> None:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE productos SET activo = FALSE WHERE id = %s", (product_id,))
                if cursor.rowcount == 0:
                    cursor.execute("SELECT id FROM productos WHERE id = %s", (product_id,))
                    if cursor.fetchone() is None:
                        raise ProductNotFound
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def activate_product(self, product_id: int) -> None:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE productos SET activo = TRUE WHERE id = %s", (product_id,))
                if cursor.rowcount == 0:
                    cursor.execute("SELECT id FROM productos WHERE id = %s", (product_id,))
                    if cursor.fetchone() is None:
                        raise ProductNotFound
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _list_options(self, table: str) -> list[CatalogOption]:
        # El nombre de tabla proviene solo de list_categories/list_brands.
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT id, nombre FROM {table} ORDER BY nombre ASC")
                return [CatalogOption(id=int(row["id"]), name=row["nombre"]) for row in cursor.fetchall()]
        finally:
            connection.close()

    def list_categories(self) -> list[CatalogOption]:
        return self._list_options("categorias")

    def list_brands(self) -> list[CatalogOption]:
        return self._list_options("marcas")

    def create_brand(self, draft: BrandDraft) -> CatalogOption:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO marcas (nombre, pais_origen) VALUES (%s, %s)",
                    (draft.name, draft.country_of_origin),
                )
                brand_id = int(cursor.lastrowid)
                cursor.execute("SELECT id, nombre FROM marcas WHERE id = %s", (brand_id,))
                row = cursor.fetchone()
            connection.commit()
            return CatalogOption(id=int(row["id"]), name=row["nombre"])
        except pymysql.err.IntegrityError as error:
            connection.rollback()
            if error.args and error.args[0] == 1062:
                raise BrandAlreadyExists from error
            raise
        finally:
            connection.close()
