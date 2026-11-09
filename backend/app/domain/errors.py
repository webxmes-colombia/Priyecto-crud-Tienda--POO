"""Errores del dominio que no dependen de HTTP ni de MySQL."""


class AccountAlreadyExists(Exception):
    """El correo ya está asociado a una cuenta o cliente."""


class SuperuserAlreadyExists(Exception):
    """El superusuario inicial ya fue creado."""


class ProductNotFound(Exception):
    """El producto solicitado no existe."""


class InvalidProductReference(Exception):
    """La categoría o la marca no existe."""


class BrandAlreadyExists(Exception):
    """Ya existe una marca con ese nombre."""


class CustomerAccountRequired(Exception):
    """La cuenta autenticada no está vinculada a un cliente comprador."""


class ProductUnavailable(Exception):
    """El producto no existe o ya no está disponible para la venta."""


class InsufficientStock(Exception):
    def __init__(self, product_name: str, available: int) -> None:
        self.product_name = product_name
        self.available = available
        super().__init__(f"Stock insuficiente para {product_name}; disponibles: {available}.")
