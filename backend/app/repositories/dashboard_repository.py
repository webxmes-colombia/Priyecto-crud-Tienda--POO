"""Consultas agregadas para el dashboard de administración."""

from collections.abc import Callable

from pymysql.connections import Connection

from app.domain.dashboard import DashboardSummary


class MySQLDashboardRepository:
    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    def get_summary(self) -> DashboardSummary:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT
                           (SELECT COUNT(*) FROM productos) AS products_total,
                           (SELECT COUNT(*) FROM productos WHERE activo = TRUE) AS products_active,
                           (SELECT COUNT(*) FROM productos WHERE activo = TRUE AND stock <= 5) AS products_low_stock,
                           (SELECT COUNT(*) FROM clientes) AS customers_total,
                           (SELECT COUNT(*) FROM pedidos) AS orders_total,
                           (SELECT COUNT(*) FROM pedidos WHERE estado NOT IN ('entregado', 'cancelado')) AS orders_pending,
                           (SELECT COUNT(*) FROM promociones
                            WHERE activa = TRUE AND empieza_en <= NOW() AND termina_en >= NOW()) AS promotions_active"""
                )
                row = cursor.fetchone()
                return DashboardSummary(**{key: int(value or 0) for key, value in row.items()})
        finally:
            connection.close()
