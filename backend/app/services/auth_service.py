"""Casos de uso de registro e inicio de sesión."""

from app.core.security import create_access_token, hash_password, read_access_token, verify_password
from app.domain.accounts import Account, CustomerRegistration
from app.domain.errors import AccountAlreadyExists
from app.domain.repositories import AuthRepository


class EmailAlreadyRegistered(Exception):
    """El correo ya pertenece a una cuenta o cliente registrado."""


class InvalidCredentials(Exception):
    """Correo, contraseña o estado de cuenta no válidos."""


class AuthService:
    """Coordina reglas de autenticación sin depender de MySQL ni HTTP."""

    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    def register_customer(self, registration: CustomerRegistration) -> tuple[Account, str]:
        email = registration.email.strip().lower()
        normalized = CustomerRegistration(
            name=registration.name.strip(),
            email=email,
            password=registration.password,
            phone=registration.phone.strip(),
            address=registration.address.strip(),
        )
        if self._repository.find_by_email(email):
            raise EmailAlreadyRegistered
        try:
            account = self._repository.create_customer(normalized, hash_password(normalized.password))
        except AccountAlreadyExists as error:
            # Cubre una carrera en la que dos registros usan el mismo correo.
            raise EmailAlreadyRegistered from error
        return account, create_access_token(account.id)

    def login(self, email: str, password: str) -> tuple[Account, str]:
        account = self._repository.find_by_email(email.strip().lower())
        if account is None or not account.active or not verify_password(password, account.password_hash):
            raise InvalidCredentials
        return account, create_access_token(account.id)

    def get_account_from_token(self, token: str) -> Account | None:
        account_id = read_access_token(token)
        if account_id is None:
            return None
        account = self._repository.find_by_id(account_id)
        return account if account and account.active else None
