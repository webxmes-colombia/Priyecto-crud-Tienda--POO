"""Endpoints HTTP para registro e inicio de sesión."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

from app.core.dependencies import get_auth_service
from app.domain.accounts import Account, CustomerRegistration
from app.services.auth_service import AuthService, EmailAlreadyRegistered, InvalidCredentials


router = APIRouter(prefix="/api/auth", tags=["Autenticación"])
bearer_scheme = HTTPBearer(auto_error=False)
EMAIL_PATTERN = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"


class CustomerRegistrationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=150, pattern=EMAIL_PATTERN)
    password: str = Field(min_length=8, max_length=128)
    phone: str = Field(min_length=7, max_length=30)
    address: str = Field(min_length=5, max_length=200)

    @field_validator("name", "email", "phone", "address", mode="before")
    @classmethod
    def strip_non_secret_fields(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=150, pattern=EMAIL_PATTERN)
    password: str = Field(min_length=1, max_length=128)


class AccountResponse(BaseModel):
    id: int
    name: str | None
    email: str
    phone: str | None
    address: str | None
    role: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AccountResponse


def _account_response(account: Account) -> AccountResponse:
    return AccountResponse(
        id=account.id,
        name=account.name,
        email=account.email,
        phone=account.phone,
        address=account.address,
        role=account.role,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_customer(
    payload: CustomerRegistrationRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        registration = CustomerRegistration(
            name=payload.name,
            email=payload.email.strip().lower(),
            password=payload.password,
            phone=payload.phone,
            address=payload.address,
        )
        account, token = service.register_customer(registration)
    except EmailAlreadyRegistered as error:
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado.") from error
    return AuthResponse(access_token=token, user=_account_response(account))


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        account, token = service.login(payload.email.strip().lower(), payload.password)
    except InvalidCredentials as error:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos, o cuenta inactiva.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    return AuthResponse(access_token=token, user=_account_response(account))


@router.get("/me", response_model=AccountResponse)
def current_account(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Falta el token de acceso.", headers={"WWW-Authenticate": "Bearer"})
    account = service.get_account_from_token(credentials.credentials)
    if account is None:
        raise HTTPException(status_code=401, detail="Token inválido o cuenta inactiva.", headers={"WWW-Authenticate": "Bearer"})
    return _account_response(account)
