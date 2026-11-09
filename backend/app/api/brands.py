"""Rutas protegidas para administrar marcas del catálogo."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.core.access_control import require_permission
from app.core.dependencies import get_catalog_service
from app.domain.accounts import Account
from app.domain.catalog import BrandDraft, CatalogOption
from app.domain.errors import BrandAlreadyExists
from app.services.catalog_service import CatalogService


router = APIRouter(prefix="/api/admin/brands", tags=["Marcas - administración"])


class BrandRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    country_of_origin: str | None = Field(default=None, max_length=80)


class BrandResponse(BaseModel):
    id: int
    name: str


@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    payload: BrandRequest,
    account: Annotated[Account, Depends(require_permission("productos.gestionar"))],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> BrandResponse:
    try:
        brand = service.create_brand(
            BrandDraft(name=payload.name, country_of_origin=payload.country_of_origin)
        )
    except BrandAlreadyExists as error:
        raise HTTPException(status_code=409, detail="Ya existe una marca con ese nombre.") from error
    return BrandResponse(id=brand.id, name=brand.name)
