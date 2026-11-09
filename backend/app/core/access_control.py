"""Dependencias reutilizables para autenticar y autorizar rutas."""

from typing import Annotated, Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.dependencies import get_auth_service, get_authorization_service
from app.domain.accounts import Account
from app.services.auth_service import AuthService
from app.services.authorization_service import AuthorizationService


bearer_scheme = HTTPBearer(auto_error=False)


def require_permission(permission_code: str) -> Callable:
    """Crea un guard que exige cuenta activa y permiso específico."""
    def permission_guard(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    ) -> Account:
        if credentials is None:
            raise HTTPException(status_code=401, detail="Falta el token de acceso.", headers={"WWW-Authenticate": "Bearer"})
        account = auth_service.get_account_from_token(credentials.credentials)
        if account is None:
            raise HTTPException(status_code=401, detail="Token inválido o cuenta inactiva.", headers={"WWW-Authenticate": "Bearer"})
        if not authorization_service.allows(account.id, permission_code):
            raise HTTPException(status_code=403, detail="No tienes permiso para realizar esta acción.")
        return account

    return permission_guard
