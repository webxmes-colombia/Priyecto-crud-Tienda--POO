"""Tipos del dominio relacionados con las cuentas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerRegistration:
    name: str
    email: str
    password: str
    phone: str
    address: str


@dataclass(frozen=True)
class Account:
    id: int
    email: str
    role: str
    active: bool
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    password_hash: str | None = None
