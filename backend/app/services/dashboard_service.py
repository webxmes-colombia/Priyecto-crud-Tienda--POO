"""Caso de uso para consultar los indicadores administrativos."""

from app.domain.dashboard import DashboardSummary
from app.domain.repositories import DashboardRepository


class DashboardService:
    def __init__(self, repository: DashboardRepository) -> None:
        self._repository = repository

    def get_summary(self) -> DashboardSummary:
        return self._repository.get_summary()
