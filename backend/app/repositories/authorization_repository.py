"""Consultas MySQL para comprobar permisos efectivos."""

from collections.abc import Callable

from pymysql.connections import Connection


class MySQLAuthorizationRepository:
    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    def has_permission(self, account_id: int, permission_code: str) -> bool:
        connection = self._connection_factory()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT 1
                       FROM usuarios AS u
                       INNER JOIN rol_permisos AS rp ON rp.rol_id = u.rol_id
                       INNER JOIN permisos AS p ON p.id = rp.permiso_id
                       WHERE u.id = %s AND u.activo = TRUE AND p.codigo = %s
                       LIMIT 1""",
                    (account_id, permission_code),
                )
                return cursor.fetchone() is not None
        finally:
            connection.close()
