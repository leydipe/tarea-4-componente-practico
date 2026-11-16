# Importamos las clases necesarias para integrar cliente, servicio y excepciones
from entidad import EntidadBase
from cliente import Cliente
from servicios import Servicio
from excepciones import ServicioNoDisponibleError, ReservaInvalidaError, DatoInvalidoError, registrar_log

# Clase Reserva que vincula un Cliente con un Servicio
class Reserva(EntidadBase):
    """Gestiona el ciclo de vida, estados y costos de una reserva."""

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
# Inicializamos el ID de la reserva
        super().__init__(id_reserva)
# Validamos que los objetos recibidos sean instancias válidas
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Se requiere un objeto Cliente válido para la reserva.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Se requiere un objeto Servicio válido para la reserva.")
        
# Asignamos los atributos de la reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"
        self.costo_total = 0.0

# Método para procesar y confirmar la reserva usando try/except/else/finally y encadenamiento
    def confirmar_reserva(self, impuesto: float = 0.19, descuento: float = 0.0):
        try:
# Verificamos si el servicio se encuentra libre
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre}' ya está ocupado.")
            
# Calculamos el costo usando el método sobrecargado del servicio
            self.costo_total = self.servicio.calcular_costo_detallado(self.duracion, impuesto, descuento)
            
        except (DatoInvalidoError, ServicioNoDisponibleError) as error_original:
# Si algo falla, marcamos la reserva como FALLIDA
            self.estado = "FALLIDA"
# Encadenamos la excepción original dentro de ReservaInvalidaError usando 'from'
            raise ReservaInvalidaError(f"No se pudo confirmar la reserva {self.id}") from error_original
            
        else:
# El bloque else se ejecuta SOLO si el bloque try no lanzó ningún error
            self.estado = "CONFIRMADA"
# Cambiamos el estado del servicio a ocupado
            self.servicio.disponible = False
            registrar_log("INFO", f"Reserva {self.id} CONFIRMADA para {self.cliente.nombre}. Total: ${self.costo_total}")
            
        finally:
# El bloque finally se ejecuta siempre, haya éxito o error
            registrar_log("AUDIT", f"Procesamiento finalizado para reserva {self.id} | Estado final: {self.estado}")

# Método para cancelar una reserva confirmada y liberar el servicio
    def cancelar_reserva(self):
# Validamos que solo se puedan cancelar reservas que estén confirmadas
        if self.estado != "CONFIRMADA":
            raise ReservaInvalidaError(f"La reserva {self.id} no se puede cancelar porque su estado es {self.estado}.")
# Actualizamos estado y liberamos el servicio
        self.estado = "CANCELADA"
        self.servicio.disponible = True
        registrar_log("INFO", f"Reserva {self.id} CANCELADA. El servicio {self.servicio.id} vuelve a estar disponible.")

# Implementación obligatoria del método abstracto
    def obtener_resumen(self) -> str:
        return (f"Reserva [{self.id}] | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} ({self.duracion}h) | "
                f"Estado: {self.estado} | Total: ${self.costo_total}")
