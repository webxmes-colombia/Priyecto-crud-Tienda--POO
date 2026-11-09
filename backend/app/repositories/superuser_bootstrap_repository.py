"""Persistencia transaccional para crear el superusuario inicial."""

from collections.abc import Callable

import pymysql
from pymysql.connections import Connection

from app.domain.errors import AccountAlreadyExists, SuperuserAlreadyExists


class MySQLSuperuserBootstrapRepository:
    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    def create_first_superuser(self, email: str, password_hash: str) -> int:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                # El bloqueo de la fila de rol serializa dos intentos simultáneos.
                cursor.execute("SELECT id FROM roles WHERE nombre = %s FOR UPDATE", ("superusuario",))
                role_row = cursor.fetchone()
                if role_row is None:
                    raise RuntimeError("No existe el rol superusuario. Inicializa la migración de comercio.")

                cursor.execute(
                    "SELECT id FROM usuarios WHERE rol_id = %s LIMIT 1",
                    (role_row["id"],),
                )
                if cursor.fetchone() is not None:
                    raise SuperuserAlreadyExists

                cursor.execute("SELECT id FROM usuarios WHERE correo = %s LIMIT 1", (email,))
                if cursor.fetchone() is not None:
                    raise AccountAlreadyExists

                cursor.execute(
                    """INSERT INTO usuarios (cliente_id, rol_id, correo, password_hash)
                       VALUES (NULL, %s, %s, %s)""",
                    (role_row["id"], email, password_hash),
                )
                account_id = int(cursor.lastrowid)
            connection.commit()
            return account_id
        except Exception as error:
            connection.rollback()
            if isinstance(error, pymysql.err.IntegrityError) and error.args and error.args[0] == 1062:
                raise AccountAlreadyExists from error
            raise
        finally:
            connection.close()
