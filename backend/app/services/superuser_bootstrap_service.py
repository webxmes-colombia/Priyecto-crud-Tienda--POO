"""Validación del caso de uso de creación del primer superusuario."""

import re

from app.core.security import hash_password
from app.domain.errors import AccountAlreadyExists, SuperuserAlreadyExists
from app.domain.repositories import SuperuserBootstrapRepository


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class SuperuserBootstrapService:
    def __init__(self, repository: SuperuserBootstrapRepository) -> None:
        self._repository = repository

    def create_first_superuser(self, email: str, password: str, confirmation: str) -> int:
        normalized_email = email.strip().lower()
        if not EMAIL_PATTERN.fullmatch(normalized_email):
            raise ValueError("Ingresa un correo válido.")
        if len(password) < 12:
            raise ValueError("La contraseña del superusuario debe tener al menos 12 caracteres.")
        if password != confirmation:
            raise ValueError("Las contraseñas no coinciden.")

        try:
            return self._repository.create_first_superuser(
                normalized_email,
                hash_password(password),
            )
        except SuperuserAlreadyExists as error:
            raise ValueError("Ya existe un superusuario. No se creó otra cuenta.") from error
        except AccountAlreadyExists as error:
            raise ValueError("Ese correo ya está asociado a otra cuenta.") from error
