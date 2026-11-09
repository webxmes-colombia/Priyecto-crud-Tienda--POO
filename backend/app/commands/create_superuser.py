"""Comando interactivo para crear el primer superusuario."""

from getpass import getpass

from app.database import obtener_conexion
from app.repositories.superuser_bootstrap_repository import MySQLSuperuserBootstrapRepository
from app.services.superuser_bootstrap_service import SuperuserBootstrapService


def main() -> None:
    email = input("Correo del superusuario: ")
    password = getpass("Contraseña (mínimo 12 caracteres): ")
    confirmation = getpass("Confirma la contraseña: ")

    repository = MySQLSuperuserBootstrapRepository(obtener_conexion)
    service = SuperuserBootstrapService(repository)
    try:
        account_id = service.create_first_superuser(email, password, confirmation)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    print(f"Superusuario creado. Identificador de cuenta: {account_id}")


if __name__ == "__main__":
    main()
