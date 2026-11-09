"""Tipos del dominio para catálogo e inventario."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ProductDraft:
    name: str
    description: str | None
    price: Decimal
    stock: int
    category_id: int
    brand_id: int


@dataclass(frozen=True)
class Product:
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
    created_at: datetime


@dataclass(frozen=True)
class CatalogOption:
    id: int
    name: str


@dataclass(frozen=True)
class BrandDraft:
    name: str
    country_of_origin: str | None = None
