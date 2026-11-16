"""Módulo de excepciones personalizadas - Software FJ.

Jerarquía:

    ErrorSoftwareFJ                      (base, E000)
    ├── DatoInvalidoError                (E100)
    │   └── ClienteInvalidoError         (E110)
    ├── ParametroFaltanteError           (E120)
    ├── ServicioError                    (E200)
    │   ├── ServicioInvalidoError        (E210)  creación/parámetros incorrectos
    │   └── ServicioNoDisponibleError    (E220)
    ├── ReservaError                     (E300)
    │   ├── ReservaInvalidaError         (E310)
    │   ├── OperacionNoPermitidaError    (E320)  p. ej. cancelar una reserva ya cancelada
    │   └── ProcesamientoReservaError    (E330)  envuelve otro error (encadenamiento)
    ├── CalculoInconsistenteError        (E400)
    └── EntidadNoEncontradaError         (E500)  cliente/servicio/reserva no existe

También expone `registrar_log(nivel, mensaje)` porque el resto del equipo
lo importa desde aquí: `from excepciones import registrar_log`.

Todas se pueden capturar con `except ErrorSoftwareFJ`, o de forma específica.

Encadenamiento: usar `raise NuevoError(...) from error_original` para conservar
la causa. El logger la registra automáticamente.
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base de todo el sistema."""

    codigo = "E000"

    def __init__(self, mensaje="Error general del sistema", detalle=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.detalle = detalle

    def __str__(self):
        base = f"[{self.codigo}] {self.mensaje}"
        return f"{base} ({self.detalle})" if self.detalle else base


# --- Datos y parámetros -----------------------------------------------------
class DatoInvalidoError(ErrorSoftwareFJ):
    """Un dato no cumple las reglas de validación."""

    codigo = "E100"


class ClienteInvalidoError(DatoInvalidoError):
    """Datos de cliente incorrectos (nombre, documento, correo, teléfono...)."""

    codigo = "E110"


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Falta un parámetro obligatorio."""

    codigo = "E120"

    def __init__(self, parametro, detalle=None):
        super().__init__(f"Falta el parámetro obligatorio '{parametro}'", detalle)
        self.parametro = parametro


# --- Servicios --------------------------------------------------------------
class ServicioError(ErrorSoftwareFJ):
    """Error general relacionado con servicios."""

    codigo = "E200"


class ServicioInvalidoError(ServicioError):
    """Creación de servicio incorrecta o parámetros inválidos."""

    codigo = "E210"


class ServicioNoDisponibleError(ServicioError):
    """El servicio existe pero no se puede reservar en este momento."""

    codigo = "E220"


# --- Reservas ---------------------------------------------------------------
class ReservaError(ErrorSoftwareFJ):
    """Error general relacionado con reservas."""

    codigo = "E300"


class ReservaInvalidaError(ReservaError):
    """Intento de reserva incorrecto (duración, cliente o servicio inválidos)."""

    codigo = "E310"


class OperacionNoPermitidaError(ReservaError):
    """La operación no es válida en el estado actual de la reserva."""

    codigo = "E320"


class ProcesamientoReservaError(ReservaError):
    """Falló el procesamiento de una reserva (suele encadenar otra causa)."""

    codigo = "E330"


# --- Cálculos ---------------------------------------------------------------
class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Resultado de un cálculo inconsistente (costo negativo, descuento > 100%...)."""

    codigo = "E400"


# --- Búsquedas --------------------------------------------------------------
class EntidadNoEncontradaError(ErrorSoftwareFJ):
    """No existe el cliente, servicio o reserva buscado."""

    codigo = "E500"


# --- Acceso al logger -------------------------------------------------------
def registrar_log(nivel, mensaje, origen="app"):
    """Escribe una línea en el archivo de logs (INFO, WARNING, ERROR, AUDIT...).

    El import va dentro de la función para evitar un import circular,
    ya que registro_logs.py también importa este módulo.
    """
    from registro_logs import logger

    logger.escribir(nivel, mensaje, origen)
