"""Punto de composición: conecta implementaciones concretas con servicios."""

from app.database import obtener_conexion
from app.repositories.catalog_repository import MySQLCatalogRepository
from app.repositories.authorization_repository import MySQLAuthorizationRepository
from app.repositories.auth_repository import MySQLAuthRepository
from app.repositories.dashboard_repository import MySQLDashboardRepository
from app.repositories.order_repository import MySQLOrderRepository
from app.services.authorization_service import AuthorizationService
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.catalog_service import CatalogService
from app.services.order_service import OrderService


def get_auth_service() -> AuthService:
    repository = MySQLAuthRepository(obtener_conexion)
    return AuthService(repository)


def get_authorization_service() -> AuthorizationService:
    repository = MySQLAuthorizationRepository(obtener_conexion)
    return AuthorizationService(repository)


def get_dashboard_service() -> DashboardService:
    repository = MySQLDashboardRepository(obtener_conexion)
    return DashboardService(repository)


def get_catalog_service() -> CatalogService:
    repository = MySQLCatalogRepository(obtener_conexion)
    return CatalogService(repository)


def get_order_service() -> OrderService:
    repository = MySQLOrderRepository(obtener_conexion)
    return OrderService(repository)
