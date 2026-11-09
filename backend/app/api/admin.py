"""Rutas administrativas protegidas por permisos."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.access_control import require_permission
from app.core.dependencies import get_dashboard_service
from app.domain.accounts import Account
from app.domain.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService


router = APIRouter(prefix="/api/admin", tags=["Administración"])


class DashboardSummaryResponse(BaseModel):
    products_total: int
    products_active: int
    products_low_stock: int
    customers_total: int
    orders_total: int
    orders_pending: int
    promotions_active: int


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    account: Annotated[Account, Depends(require_permission("usuarios.gestionar"))],
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardSummary:
    return service.get_summary()
