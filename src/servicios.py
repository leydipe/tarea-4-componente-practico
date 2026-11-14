from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, overload


class Servicio(ABC):
    """Representa una entidad abstracta de servicio disponible en Software FJ."""

    def __init__(self, codigo: str, nombre: str, descripcion: str, tarifa_base: float, duracion_horas: float):
        self.codigo = self._validar_texto(codigo, "codigo")
        self.nombre = self._validar_texto(nombre, "nombre")
        self.descripcion = self._validar_texto(descripcion, "descripcion")
        self.tarifa_base = self._validar_numero(tarifa_base, "tarifa_base", minimo=0)
        self.duracion_horas = self._validar_numero(duracion_horas, "duracion_horas", minimo=0)

    @staticmethod
    def _validar_texto(valor: Any, nombre: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"El campo {nombre} es obligatorio.")
        return valor.strip()

    @staticmethod
    def _validar_numero(valor: Any, nombre: str, minimo: float = 0) -> float:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError(f"El campo {nombre} debe ser numérico.")

        valor = float(valor)
        if valor < minimo:
            raise ValueError(f"El campo {nombre} no puede ser menor que {minimo}.")
        return valor

    @staticmethod
    def _aplicar_descuento_y_impuesto(subtotal: float, descuento: float, impuesto: float) -> float:
        descuento = max(0.0, float(descuento))
        impuesto = max(0.0, float(impuesto))

        if descuento > 100:
            raise ValueError("El descuento no puede superar el 100%.")
        if impuesto > 100:
            raise ValueError("El impuesto no puede superar el 100%.")

        subtotal_con_descuento = subtotal * (1 - (descuento / 100))
        total = subtotal_con_descuento * (1 + (impuesto / 100))
        return round(total, 2)

    @overload
    def calcular_costo(self, horas: float, descuento: float = 0, impuesto: float = 19) -> float: ...

    @overload
    def calcular_costo(self, cantidad: int, descuento: float = 0, impuesto: float = 19) -> float: ...

    @abstractmethod
    def validar_parametros(self, *args, **kwargs) -> None:
        """Valida los parámetros de entrada para el cálculo del costo."""

    @abstractmethod
    def descripcion_servicio(self) -> str:
        """Devuelve la descripción del servicio."""

    def obtener_informacion(self) -> dict:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "tarifa_base": self.tarifa_base,
            "duracion_horas": self.duracion_horas,
        }

    def mostrar_informacion(self) -> None:
        print(f"Código: {self.codigo}")
        print(f"Nombre: {self.nombre}")
        print(f"Descripción: {self.descripcion}")
        print(f"Tarifa base: ${self.tarifa_base:,.2f}")
        print(f"Duración estimada: {self.duracion_horas} horas")

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre}"


class SalaReserva(Servicio):
    """Servicio de reserva de salas con cálculo por horas."""

    def __init__(self, codigo: str, nombre: str, descripcion: str, tarifa_base: float, duracion_horas: float):
        super().__init__(codigo, nombre, descripcion, tarifa_base, duracion_horas)

    def validar_parametros(self, horas: float | int, descuento: float = 0, impuesto: float = 19) -> None:
        if not isinstance(horas, (int, float)) or isinstance(horas, bool):
            raise TypeError("Las horas deben ser un valor numérico.")
        if horas <= 0:
            raise ValueError("La cantidad de horas debe ser mayor que cero.")
        if descuento < 0:
            raise ValueError("El descuento no puede ser negativo.")
        if impuesto < 0:
            raise ValueError("El impuesto no puede ser negativo.")

    def calcular_costo(self, horas: float | int | None = None, descuento: float = 0, impuesto: float = 19) -> float:
        horas = self.duracion_horas if horas is None else float(horas)
        self.validar_parametros(horas, descuento, impuesto)
        subtotal = self.tarifa_base * horas
        return self._aplicar_descuento_y_impuesto(subtotal, descuento, impuesto)

    def descripcion_servicio(self) -> str:
        return (
            f"Sala reservada: {self.nombre}. "
            f"Incluye espacio para reuniones, acceso a equipos y soporte básico. "
            f"Tarifa base por hora: ${self.tarifa_base:,.2f}."
        )


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos, calculado por cantidad de unidades."""

    def __init__(self, codigo: str, nombre: str, descripcion: str, tarifa_base: float, duracion_horas: float):
        super().__init__(codigo, nombre, descripcion, tarifa_base, duracion_horas)

    def validar_parametros(self, cantidad: float | int, descuento: float = 0, impuesto: float = 19) -> None:
        if not isinstance(cantidad, (int, float)) or isinstance(cantidad, bool):
            raise TypeError("La cantidad de equipos debe ser numérica.")
        if cantidad <= 0:
            raise ValueError("La cantidad de equipos debe ser mayor que cero.")
        if descuento < 0:
            raise ValueError("El descuento no puede ser negativo.")
        if impuesto < 0:
            raise ValueError("El impuesto no puede ser negativo.")

    def calcular_costo(self, cantidad: float | int | None = None, descuento: float = 0, impuesto: float = 19) -> float:
        cantidad = 1 if cantidad is None else float(cantidad)
        self.validar_parametros(cantidad, descuento, impuesto)
        subtotal = self.tarifa_base * cantidad
        return self._aplicar_descuento_y_impuesto(subtotal, descuento, impuesto)

    def descripcion_servicio(self) -> str:
        return (
            f"Alquiler de equipos: {self.nombre}. "
            f"Disponibilidad para uso técnico y operativo. "
            f"Tarifa base por unidad: ${self.tarifa_base:,.2f}."
        )


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría con cálculo por horas y nivel de especialización."""

    def __init__(self, codigo: str, nombre: str, descripcion: str, tarifa_base: float, duracion_horas: float, nivel: str = "básico"):
        super().__init__(codigo, nombre, descripcion, tarifa_base, duracion_horas)
        self.nivel = self._validar_texto(nivel, "nivel")

    def validar_parametros(self, horas: float | int, descuento: float = 0, impuesto: float = 19) -> None:
        if not isinstance(horas, (int, float)) or isinstance(horas, bool):
            raise TypeError("Las horas de asesoría deben ser numéricas.")
        if horas <= 0:
            raise ValueError("Las horas de asesoría deben ser mayores que cero.")
        if descuento < 0:
            raise ValueError("El descuento no puede ser negativo.")
        if impuesto < 0:
            raise ValueError("El impuesto no puede ser negativo.")

    def calcular_costo(self, horas: float | int | None = None, descuento: float = 0, impuesto: float = 19) -> float:
        horas = self.duracion_horas if horas is None else float(horas)
        self.validar_parametros(horas, descuento, impuesto)
        subtotal = self.tarifa_base * horas
        return self._aplicar_descuento_y_impuesto(subtotal, descuento, impuesto)

    def descripcion_servicio(self) -> str:
        return (
            f"Asesoría especializada: {self.nombre}. "
            f"Nivel: {self.nivel}. "
            f"Tarifa base por hora: ${self.tarifa_base:,.2f}."
        )
