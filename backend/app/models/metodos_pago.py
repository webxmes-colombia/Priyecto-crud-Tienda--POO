from abc import ABC, abstractmethod


class MetodoPago(ABC):
    @abstractmethod
    def pagar(self, monto):
        pass


class PagoEfectivo(MetodoPago):
    def pagar(self, monto):
        print(f"Pago en efectivo: ${monto}")


class PagoTarjeta(MetodoPago):
    def pagar(self, monto):
        print(f"Pago con tarjeta: ${monto}")


class PagoNequi(MetodoPago):
    def pagar(self, monto):
        print(f"Pago con tarjeta: ${monto}")



class PagoDaviplaya(MetodoPago):
    def pagar(self, monto):
        print(f"Pago con Daviplaya: ${monto}")


class PagoBreve(MetodoPago):
    def pagar(self, monto):
        print(f"Pago con Breve: ${monto}")
