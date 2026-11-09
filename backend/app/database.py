"""Configuración y comprobación de conexión a MySQL."""

import os

import pymysql
from pymysql.connections import Connection


def obtener_conexion() -> Connection:
    """Abre una conexión usando las variables de entorno del contenedor."""
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "tienda_repuestos"),
        charset="utf8mb4",
        connect_timeout=3,
        cursorclass=pymysql.cursors.DictCursor,
    )
