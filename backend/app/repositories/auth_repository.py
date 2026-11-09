"""Persistencia MySQL para cuentas y clientes."""

from collections.abc import Callable

import pymysql
from pymysql.connections import Connection

from app.domain.accounts import Account, CustomerRegistration
from app.domain.errors import AccountAlreadyExists


class MySQLAuthRepository:
    """Implementación MySQL del contrato de autenticación."""

    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    @staticmethod
    def _to_account(row: dict | None, include_password: bool = False) -> Account | None:
        if row is None:
            return None
        return Account(
            id=int(row["id"]),
            email=row["correo"],
            role=row["rol"],
            active=bool(row["activo"]),
            name=row.get("nombre"),
            phone=row.get("telefono"),
            address=row.get("direccion"),
            password_hash=row.get("password_hash") if include_password else None,
        )

    def create_customer(self, registration: CustomerRegistration, password_hash: str) -> Account:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM roles WHERE nombre = %s", ("cliente",))
                role_row = cursor.fetchone()
                if role_row is None:
                    raise RuntimeError("No existe el rol cliente. Inicializa la migración de comercio.")

                cursor.execute("SELECT id FROM clientes WHERE correo = %s LIMIT 1", (registration.email,))
                existing_customer = cursor.fetchone()
                if existing_customer:
                    customer_id = existing_customer["id"]
                    cursor.execute(
                        """UPDATE clientes
                           SET nombre = %s, telefono = %s, direccion = %s
                           WHERE id = %s""",
                        (registration.name, registration.phone, registration.address, customer_id),
                    )
                else:
                    cursor.execute(
                        """INSERT INTO clientes (nombre, correo, telefono, direccion)
                           VALUES (%s, %s, %s, %s)""",
                        (registration.name, registration.email, registration.phone, registration.address),
                    )
                    customer_id = cursor.lastrowid
                cursor.execute(
                    """INSERT INTO usuarios (cliente_id, rol_id, correo, password_hash)
                       VALUES (%s, %s, %s, %s)""",
                    (customer_id, role_row["id"], registration.email, password_hash),
                )
                account_id = cursor.lastrowid
            connection.commit()
        except Exception as error:
            connection.rollback()
            # MySQL 1062 identifica una violación de índice único.
            if isinstance(error, pymysql.err.IntegrityError) and error.args and error.args[0] == 1062:
                raise AccountAlreadyExists from error
            raise
        finally:
            connection.close()

        return Account(
            id=int(account_id),
            email=registration.email,
            role="cliente",
            active=True,
            name=registration.name,
            phone=registration.phone,
            address=registration.address,
        )

    def find_by_email(self, email: str) -> Account | None:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT u.id, u.correo, u.password_hash, u.activo, r.nombre AS rol,
                              COALESCE(u.nombre, c.nombre) AS nombre, c.telefono, c.direccion
                       FROM usuarios AS u
                       INNER JOIN roles AS r ON r.id = u.rol_id
                       LEFT JOIN clientes AS c ON c.id = u.cliente_id
                       WHERE u.correo = %s LIMIT 1""",
                    (email,),
                )
                return self._to_account(cursor.fetchone(), include_password=True)
        finally:
            connection.close()

    def find_by_id(self, account_id: int) -> Account | None:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT u.id, u.correo, u.activo, r.nombre AS rol,
                              COALESCE(u.nombre, c.nombre) AS nombre, c.telefono, c.direccion
                       FROM usuarios AS u
                       INNER JOIN roles AS r ON r.id = u.rol_id
                       LEFT JOIN clientes AS c ON c.id = u.cliente_id
                       WHERE u.id = %s LIMIT 1""",
                    (account_id,),
                )
                return self._to_account(cursor.fetchone())
        finally:
            connection.close()
