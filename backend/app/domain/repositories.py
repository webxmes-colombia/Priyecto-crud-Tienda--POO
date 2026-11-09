"""Contratos que necesita el caso de uso de autenticación."""

from typing import Protocol

from app.domain.accounts import Account, CustomerRegistration
from app.domain.catalog import BrandDraft, CatalogOption, Product, ProductDraft
from app.domain.dashboard import DashboardSummary
from app.domain.orders import Order, OrderDraft


class AuthRepository(Protocol):
    """Operaciones de persistencia requeridas por autenticación."""

    def create_customer(self, registration: CustomerRegistration, password_hash: str) -> Account:
        """Crea el cliente y su cuenta en una sola transacción."""
        ...

    def find_by_email(self, email: str) -> Account | None:
        """Busca una cuenta por correo, incluyendo el hash de contraseña."""
        ...

    def find_by_id(self, account_id: int) -> Account | None:
        """Busca una cuenta activa por identificador."""
        ...


class AuthorizationRepository(Protocol):
    """Contrato de lectura para permisos asignados a una cuenta."""

    def has_permission(self, account_id: int, permission_code: str) -> bool:
        ...


class DashboardRepository(Protocol):
    """Contrato para los datos agregados del dashboard administrativo."""

    def get_summary(self) -> DashboardSummary:
        ...


class SuperuserBootstrapRepository(Protocol):
    """Contrato para la creación inicial y controlada del superusuario."""

    def create_first_superuser(self, email: str, password_hash: str) -> int:
        ...


class CatalogRepository(Protocol):
    """Contrato para consultas de catálogo y administración de productos."""

    def list_products(self, *, include_inactive: bool, category_id: int | None, brand_id: int | None,
                      search: str | None, limit: int, offset: int) -> list[Product]:
        ...

    def get_product(self, product_id: int) -> Product | None:
        ...

    def create_product(self, draft: ProductDraft) -> Product:
        ...

    def update_product(self, product_id: int, draft: ProductDraft) -> Product:
        ...

    def deactivate_product(self, product_id: int) -> None:
        ...

    def activate_product(self, product_id: int) -> None:
        ...

    def list_categories(self) -> list[CatalogOption]:
        ...

    def list_brands(self) -> list[CatalogOption]:
        ...

    def create_brand(self, draft: BrandDraft) -> CatalogOption:
        ...


class OrderRepository(Protocol):
    """Contrato para las operaciones de compra y consulta de pedidos."""

    def create_order(self, account_id: int, draft: OrderDraft) -> Order:
        ...
