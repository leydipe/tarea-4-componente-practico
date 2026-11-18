# Importamos las clases de los módulos desarrollados por el equipo
from cliente import Cliente
from servicios import Servicio
from registro_logs import logger
from excepciones import (
    DatoInvalidoError,
    ClienteInvalidoError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    ProcesamientoReservaError,
    CalculoInconsistenteError,
)


class Reserva:
    """Gestiona la integración entre Cliente y Servicio, estados y cálculo de costos."""

# Estados permitidos en el ciclo de vida de una reserva
    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "FALLIDA")

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion_o_cantidad: float | int):
# Validamos que el ID de la reserva sea un texto válido
        if not isinstance(id_reserva, str) or not id_reserva.strip():
            raise ReservaInvalidaError("El ID de la reserva es obligatorio y no puede estar vacío.")
        self.id = id_reserva.strip()

# Validamos que el objeto recibido sea una instancia válida de Cliente
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Se debe asociar un objeto Cliente válido a la reserva.")
# Validamos que el cliente haya pasado sus propias validaciones internas
        if not getattr(cliente, "valido", True):
            raise ClienteInvalidoError(
                f"El cliente '{cliente.obtener_nombre()}' tiene datos inválidos y no puede reservar."
            )

# Validamos que el objeto recibido sea una instancia válida de Servicio
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Se debe asociar un objeto Servicio válido a la reserva.")

# Validamos que la duración o cantidad sea un número positivo
        if isinstance(duracion_o_cantidad, bool) or not isinstance(duracion_o_cantidad, (int, float)) or duracion_o_cantidad <= 0:
            raise ReservaInvalidaError("La duración o cantidad de la reserva debe ser mayor a cero.")

# Asignamos los atributos principales
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion_o_cantidad
        self.estado = "PENDIENTE"
        self.costo_total = 0.0

# Si el servicio del compañero no tiene el atributo 'disponible', se lo inicializamos en True
        if not hasattr(self.servicio, "disponible"):
            self.servicio.disponible = True

    def calcular_total(self, descuento: float = 0.0, impuesto: float = 19.0) -> float:
        """Método sobrecargado (por parámetros opcionales) que delega el cálculo al servicio."""
        try:
# Llamamos al método polimórfico calcular_costo de SalaReserva, AlquilerEquipo o AsesoriaEspecializada
            total = self.servicio.calcular_costo(self.duracion, descuento=descuento, impuesto=impuesto)
            if total < 0:
                raise CalculoInconsistenteError("El cálculo de la reserva arrojó un valor negativo.")
            return total
        except (ValueError, TypeError) as exc:
# Convertimos errores estándar de Python en nuestra excepción personalizada del sistema
            raise CalculoInconsistenteError(f"Error al calcular el costo de la reserva {self.id}", detalle=str(exc)) from exc

    def confirmar_reserva(self, descuento: float = 0.0, impuesto: float = 19.0) -> None:
        """Procesa y confirma la reserva usando bloques try/except/else/finally y encadenamiento."""
        try:
# Solo se pueden confirmar reservas que estén en estado PENDIENTE
            if self.estado != "PENDIENTE":
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar la reserva {self.id} porque está en estado '{self.estado}'."
                )

# Verificamos disponibilidad del servicio
            if not getattr(self.servicio, "disponible", True):
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.servicio.codigo} - {self.servicio.nombre}' no está disponible actualmente."
                )

# Calculamos el valor total con impuestos y descuentos
            self.costo_total = self.calcular_total(descuento=descuento, impuesto=impuesto)

        except (OperacionNoPermitidaError, ServicioNoDisponibleError, CalculoInconsistenteError, DatoInvalidoError) as error_causa:
# Si ocurre un error controlado, cambiamos el estado a FALLIDA
            self.estado = "FALLIDA"
# Encadenamos la excepción original dentro de ProcesamientoReservaError (exigido por la guía)
            error_final = ProcesamientoReservaError(
                f"Fallo al procesar la reserva {self.id}", detalle=str(error_causa)
            )
            error_final.__cause__ = error_causa
# Registramos la excepción completa y su cadena de causas en el archivo de logs
            logger.excepcion(error_final, origen="Reserva.confirmar_reserva")
            raise error_final from error_causa

        else:
# Se ejecuta únicamente si el bloque try finalizó sin errores
            self.estado = "CONFIRMADA"
            self.servicio.disponible = False
            logger.evento(
                f"Reserva {self.id} CONFIRMADA | Cliente: {self.cliente.obtener_nombre()} | "
                f"Servicio: {self.servicio.codigo} | Total: ${self.costo_total:,.2f}",
                origen="Reserva.confirmar_reserva",
            )

        finally:
# Se ejecuta siempre para dejar auditoría del intento de procesamiento
            logger.audit(
                f"Fin de procesamiento reserva {self.id} -> Estado actual: {self.estado}",
                origen="Reserva.confirmar_reserva",
            )

    def cancelar_reserva(self) -> None:
        """Cancela una reserva confirmada y libera el servicio."""
        try:
            if self.estado != "CONFIRMADA":
                raise OperacionNoPermitidaError(
                    f"Solo se pueden cancelar reservas CONFIRMADAS (estado actual: {self.estado})."
                )
        except OperacionNoPermitidaError as exc:
            logger.excepcion(exc, origen="Reserva.cancelar_reserva")
            raise
        else:
            self.estado = "CANCELADA"
            self.servicio.disponible = True
            logger.evento(
                f"Reserva {self.id} CANCELADA. Servicio {self.servicio.codigo} liberado.",
                origen="Reserva.cancelar_reserva",
            )

    def obtener_resumen(self) -> str:
        """Devuelve una descripción legible de la reserva."""
        return (
            f"Reserva [{self.id}] | Cliente: {self.cliente.obtener_nombre()} ({self.cliente.obtener_identificacion()}) | "
            f"Servicio: {self.servicio.nombre} | Cantidad/Horas: {self.duracion} | "
            f"Estado: {self.estado} | Total: ${self.costo_total:,.2f}"
        )

    def __str__(self) -> str:
        return self.obtener_resumen()
