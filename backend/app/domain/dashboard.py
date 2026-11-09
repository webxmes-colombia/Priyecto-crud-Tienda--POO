"""Datos resumidos que muestra el dashboard administrativo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DashboardSummary:
    products_total: int
    products_active: int
    products_low_stock: int
    customers_total: int
    orders_total: int
    orders_pending: int
    promotions_active: int
