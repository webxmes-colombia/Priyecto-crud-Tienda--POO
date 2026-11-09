"""Casos de uso del catálogo y gestión de productos."""

from app.domain.catalog import BrandDraft, CatalogOption, Product, ProductDraft
from app.domain.repositories import CatalogRepository


class CatalogService:
    def __init__(self, repository: CatalogRepository) -> None:
        self._repository = repository

    def list_products(self, *, include_inactive: bool = False, category_id: int | None = None,
                      brand_id: int | None = None, search: str | None = None,
                      limit: int = 50, offset: int = 0) -> list[Product]:
        return self._repository.list_products(
            include_inactive=include_inactive,
            category_id=category_id,
            brand_id=brand_id,
            search=search,
            limit=limit,
            offset=offset,
        )

    def create_product(self, draft: ProductDraft) -> Product:
        normalized = ProductDraft(
            name=draft.name.strip(),
            description=draft.description.strip() if draft.description else None,
            price=draft.price,
            stock=draft.stock,
            category_id=draft.category_id,
            brand_id=draft.brand_id,
        )
        return self._repository.create_product(normalized)

    def update_product(self, product_id: int, draft: ProductDraft) -> Product:
        normalized = ProductDraft(
            name=draft.name.strip(),
            description=draft.description.strip() if draft.description else None,
            price=draft.price,
            stock=draft.stock,
            category_id=draft.category_id,
            brand_id=draft.brand_id,
        )
        return self._repository.update_product(product_id, normalized)

    def deactivate_product(self, product_id: int) -> None:
        self._repository.deactivate_product(product_id)

    def activate_product(self, product_id: int) -> None:
        self._repository.activate_product(product_id)

    def list_categories(self) -> list[CatalogOption]:
        return self._repository.list_categories()

    def list_brands(self) -> list[CatalogOption]:
        return self._repository.list_brands()

    def create_brand(self, draft: BrandDraft) -> CatalogOption:
        normalized = BrandDraft(
            name=draft.name.strip(),
            country_of_origin=draft.country_of_origin.strip() or None if draft.country_of_origin else None,
        )
        return self._repository.create_brand(normalized)
