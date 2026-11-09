"""Tipos del dominio para crear pedidos de la tienda."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class OrderItemDraft:
    product_id: int
    quantity: int


@dataclass(frozen=True)
class OrderDraft:
    items: tuple[OrderItemDraft, ...]
    payment_method: str
    delivery_email: str
    delivery_phone: str
    delivery_address: str


@dataclass(frozen=True)
class OrderItem:
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    line_subtotal: Decimal


@dataclass(frozen=True)
class Order:
    id: int
    status: str
    payment_method: str
    payment_status: str
    subtotal: Decimal
    discount: Decimal
    shipping_cost: Decimal
    total: Decimal
    created_at: datetime
    items: tuple[OrderItem, ...]
