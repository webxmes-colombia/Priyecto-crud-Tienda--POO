"""Punto de entrada de la API de la tienda."""

import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.brands import router as brands_admin_router
from app.api.catalog import admin_router as product_admin_router
from app.api.catalog import public_router as catalog_router
from app.api.orders import router as orders_router
from app.database import obtener_conexion

# FastAPI recibe las solicitudes del frontend y devolverá respuestas JSON.
app = FastAPI(title="API de la tienda")

# El navegador permite al frontend (puerto 8080) consultar la API (puerto 8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(catalog_router)
app.include_router(product_admin_router)
app.include_router(orders_router)
app.include_router(brands_admin_router)


@app.get("/api/health")
def verificar_estado():
    """Comprueba que la API puede comunicarse con MySQL."""
    try:
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT 1 AS disponible")
                cursor.fetchone()
        finally:
            conexion.close()
    except pymysql.MySQLError as error:
        raise HTTPException(
            status_code=503,
            detail="La API está activa, pero no se pudo conectar con la base de datos.",
        ) from error

    return {"estado": "Backend y base de datos funcionando", "base_de_datos": "conectada"}
