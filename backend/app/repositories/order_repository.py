"""Creación transaccional de pedidos y actualización de existencias."""

from collections.abc import Callable
from decimal import Decimal

from pymysql.connections import Connection

from app.domain.errors import CustomerAccountRequired, InsufficientStock, ProductUnavailable
from app.domain.orders import Order, OrderDraft, OrderItem


class MySQLOrderRepository:
    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    def create_order(self, account_id: int, draft: OrderDraft) -> Order:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT cliente_id FROM usuarios WHERE id = %s AND activo = TRUE FOR UPDATE",
                    (account_id,),
                )
                account_row = cursor.fetchone()
                if account_row is None or account_row["cliente_id"] is None:
                    raise CustomerAccountRequired
                customer_id = account_row["cliente_id"]

                product_ids = sorted(item.product_id for item in draft.items)
                placeholders = ",".join(["%s"] * len(product_ids))
                cursor.execute(
                    f"""SELECT id, nombre, precio, stock, activo
                        FROM productos
                        WHERE id IN ({placeholders})
                        ORDER BY id
                        FOR UPDATE""",
                    tuple(product_ids),
                )
                products = {int(row["id"]): row for row in cursor.fetchall()}
                order_items: list[OrderItem] = []
                subtotal = Decimal("0.00")
                for item in draft.items:
                    row = products.get(item.product_id)
                    if row is None or not row["activo"]:
                        raise ProductUnavailable
                    available = int(row["stock"])
                    if available < item.quantity:
                        raise InsufficientStock(row["nombre"], available)
                    unit_price = Decimal(row["precio"])
                    line_subtotal = unit_price * item.quantity
                    subtotal += line_subtotal
                    order_items.append(
                        OrderItem(
                            product_id=item.product_id,
                            product_name=row["nombre"],
                            unit_price=unit_price,
                            quantity=item.quantity,
                            line_subtotal=line_subtotal,
                        )
                    )

                discount = Decimal("0.00")
                shipping_cost = Decimal("0.00")
                total = subtotal - discount + shipping_cost
                cursor.execute(
                    """INSERT INTO pedidos
                       (cliente_id, correo_entrega, telefono_entrega, direccion_entrega,
                        metodo_pago, subtotal, descuento, costo_envio, total)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        customer_id,
                        draft.delivery_email,
                        draft.delivery_phone,
                        draft.delivery_address,
                        draft.payment_method,
                        subtotal,
                        discount,
                        shipping_cost,
                        total,
                    ),
                )
                order_id = int(cursor.lastrowid)

                for item in order_items:
                    cursor.execute(
                        """INSERT INTO detalle_pedidos
                           (pedido_id, producto_id, producto_nombre, precio_unitario, cantidad, subtotal_linea)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (
                            order_id,
                            item.product_id,
                            item.product_name,
                            item.unit_price,
                            item.quantity,
                            item.line_subtotal,
                        ),
                    )
                    cursor.execute(
                        "UPDATE productos SET stock = stock - %s WHERE id = %s AND stock >= %s",
                        (item.quantity, item.product_id, item.quantity),
                    )
                    if cursor.rowcount != 1:
                        raise InsufficientStock(item.product_name, 0)

                cursor.execute("SELECT creado_en FROM pedidos WHERE id = %s", (order_id,))
                created_at = cursor.fetchone()["creado_en"]
            connection.commit()
            return Order(
                id=order_id,
                status="recibido",
                payment_method=draft.payment_method,
                payment_status="pendiente",
                subtotal=subtotal,
                discount=discount,
                shipping_cost=shipping_cost,
                total=total,
                created_at=created_at,
                items=tuple(order_items),
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
