"""Endpoints públicos de catálogo y administrativos de productos."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.core.access_control import require_permission
from app.core.dependencies import get_catalog_service
from app.domain.accounts import Account
from app.domain.catalog import CatalogOption, Product, ProductDraft
from app.domain.errors import InvalidProductReference, ProductNotFound
from app.services.catalog_service import CatalogService


public_router = APIRouter(prefix="/api/catalog", tags=["Catálogo"])
admin_router = APIRouter(prefix="/api/admin/products", tags=["Productos - administración"])


class ProductRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    stock: int = Field(ge=0)
    category_id: int = Field(gt=0)
    brand_id: int = Field(gt=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    category_id: int
    category_name: str
    brand_id: int
    brand_name: str
    active: bool
    created_at: str


class CatalogOptionResponse(BaseModel):
    id: int
    name: str


def _to_draft(payload: ProductRequest) -> ProductDraft:
    return ProductDraft(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        category_id=payload.category_id,
        brand_id=payload.brand_id,
    )


def _to_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id,
        category_name=product.category_name,
        brand_id=product.brand_id,
        brand_name=product.brand_name,
        active=product.active,
        created_at=product.created_at.isoformat(),
    )


def _not_found(error: ProductNotFound) -> HTTPException:
    return HTTPException(status_code=404, detail="El producto no existe.")


@public_router.get("/products", response_model=list[ProductResponse])
def list_public_products(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    category_id: int | None = Query(default=None, gt=0),
    brand_id: int | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ProductResponse]:
    products = service.list_products(
        category_id=category_id,
        brand_id=brand_id,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [_to_response(product) for product in products]


@public_router.get("/categories", response_model=list[CatalogOptionResponse])
def list_categories(service: Annotated[CatalogService, Depends(get_catalog_service)]) -> list[CatalogOption]:
    return service.list_categories()


@public_router.get("/brands", response_model=list[CatalogOptionResponse])
def list_brands(service: Annotated[CatalogService, Depends(get_catalog_service)]) -> list[CatalogOption]:
    return service.list_brands()


@admin_router.get("", response_model=list[ProductResponse])
def list_admin_products(
    account: Annotated[Account, Depends(require_permission("productos.gestionar"))],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    include_inactive: bool = False,
    category_id: int | None = Query(default=None, gt=0),
    brand_id: int | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ProductResponse]:
    products = service.list_products(
        include_inactive=include_inactive,
        category_id=category_id,
        brand_id=brand_id,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [_to_response(product) for product in products]


@admin_router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductRequest,
    account: Annotated[Account, Depends(require_permission("productos.gestionar"))],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    try:
        return _to_response(service.create_product(_to_draft(payload)))
    except InvalidProductReference as error:
        raise HTTPException(status_code=422, detail="La categoría o la marca seleccionada no existe.") from error


@admin_router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductRequest,
    account: Annotated[Account, Depends(require_permission("productos.gestionar"))],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    try:
        return _to_response(service.update_product(product_id, _to_draft(payload)))
    except ProductNotFound as error:
        raise _not_found(error) from error
    except InvalidProductReference as error:
        raise HTTPException(status_code=422, detail="La categoría o la marca seleccionada no existe.") from error


@admin_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(
    product_id: int,
    account: Annotated[Account, Depends(require_permission("productos.gestionar"))],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> Response:
    try:
        service.deactivate_product(product_id)
    except ProductNotFound as error:
        raise _not_found(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@admin_router.patch("/{product_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
def activate_product(
    product_id: int,
    account: Annotated[Account, Depends(require_permission("productos.gestionar"))],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> Response:
    try:
        service.activate_product(product_id)
    except ProductNotFound as error:
        raise _not_found(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
