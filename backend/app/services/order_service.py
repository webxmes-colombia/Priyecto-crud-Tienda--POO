"""Caso de uso para validar y registrar una compra."""

from app.domain.errors import ProductUnavailable
from app.domain.orders import Order, OrderDraft, OrderItemDraft
from app.domain.repositories import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def create_order(self, account_id: int, draft: OrderDraft) -> Order:
        if not draft.items:
            raise ValueError("El carrito está vacío.")

        quantities: dict[int, int] = {}
        for item in draft.items:
            quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity
            if quantities[item.product_id] > 99:
                raise ValueError("No se permiten más de 99 unidades del mismo producto.")
        if len(quantities) > 50:
            raise ValueError("El pedido no puede incluir más de 50 productos distintos.")

        normalized = OrderDraft(
            items=tuple(OrderItemDraft(product_id, quantity) for product_id, quantity in quantities.items()),
            payment_method=draft.payment_method,
            delivery_email=draft.delivery_email.strip().lower(),
            delivery_phone=draft.delivery_phone.strip(),
            delivery_address=draft.delivery_address.strip(),
        )
        if not normalized.delivery_email or not normalized.delivery_phone or not normalized.delivery_address:
            raise ValueError("Completa los datos de entrega antes de confirmar.")
        return self._repository.create_order(account_id, normalized)
