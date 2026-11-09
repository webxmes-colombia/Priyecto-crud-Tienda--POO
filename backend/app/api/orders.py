"""Endpoints para confirmar compras y consultar pedidos del cliente."""

from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.access_control import require_permission
from app.core.dependencies import get_order_service
from app.domain.accounts import Account
from app.domain.errors import CustomerAccountRequired, InsufficientStock, ProductUnavailable
from app.domain.orders import Order, OrderDraft, OrderItemDraft
from app.services.order_service import OrderService


router = APIRouter(prefix="/api/orders", tags=["Pedidos"])


class CheckoutItemRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=99)


class CheckoutRequest(BaseModel):
    items: list[CheckoutItemRequest] = Field(min_length=1, max_length=50)
    payment_method: Literal["contraentrega", "nequi", "daviplata"]
    delivery_email: str = Field(min_length=5, max_length=150, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    delivery_phone: str = Field(min_length=7, max_length=30)
    delivery_address: str = Field(min_length=5, max_length=200)


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    line_subtotal: Decimal


class OrderResponse(BaseModel):
    id: int
    status: str
    payment_method: str
    payment_status: str
    subtotal: Decimal
    discount: Decimal
    shipping_cost: Decimal
    total: Decimal
    created_at: str
    items: list[OrderItemResponse]


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        status=order.status,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        discount=order.discount,
        shipping_cost=order.shipping_cost,
        total=order.total,
        created_at=order.created_at.isoformat(),
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                line_subtotal=item.line_subtotal,
            )
            for item in order.items
        ],
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    payload: CheckoutRequest,
    account: Annotated[Account, Depends(require_permission("pedidos.crear"))],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    draft = OrderDraft(
        items=tuple(OrderItemDraft(item.product_id, item.quantity) for item in payload.items),
        payment_method=payload.payment_method,
        delivery_email=payload.delivery_email,
        delivery_phone=payload.delivery_phone,
        delivery_address=payload.delivery_address,
    )
    try:
        return _to_response(service.create_order(account.id, draft))
    except CustomerAccountRequired as error:
        raise HTTPException(status_code=409, detail="La cuenta debe estar vinculada a un perfil de cliente.") from error
    except InsufficientStock as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ProductUnavailable as error:
        raise HTTPException(status_code=409, detail="Uno de los productos ya no está disponible.") from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
