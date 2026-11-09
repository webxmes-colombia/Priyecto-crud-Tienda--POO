"""Reglas de autorización por permiso."""

from app.domain.repositories import AuthorizationRepository


class AuthorizationService:
    def __init__(self, repository: AuthorizationRepository) -> None:
        self._repository = repository

    def allows(self, account_id: int, permission_code: str) -> bool:
        return self._repository.has_permission(account_id, permission_code)
