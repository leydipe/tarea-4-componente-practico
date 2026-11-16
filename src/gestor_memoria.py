# Importamos las entidades y excepciones necesarias
from cliente import Cliente
from servicios import Servicio
from reserva import Reserva
from excepciones import DatoInvalidoError, EntidadNoEncontradaError, registrar_log

# Clase encargada de administrar las colecciones en memoria (listas)
class GestorSistemaFJ:
    """Administra clientes, servicios y reservas en listas internas sin base de datos."""

    def __init__(self):
# Inicializamos las tres listas vacías en memoria
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []

# Agrega un cliente validando que no exista un id duplicado
    def agregar_cliente(self, cliente: Cliente):
        if any(c.id == cliente.id for c in self._clientes):
            raise DatoInvalidoError(f"Ya existe un cliente registrado con el ID '{cliente.id}'.")
        self._clientes.append(cliente)
        registrar_log("INFO", f"Cliente agregado a memoria: {cliente.obtener_resumen()}")

# Busca un cliente por su id en la lista interna
    def buscar_cliente(self, id_cliente: str) -> Cliente:
        for cliente in self._clientes:
            if cliente.id == id_cliente:
                return cliente
        raise EntidadNoEncontradaError(f"No se encontró ningún cliente con ID '{id_cliente}'.")

# Agrega un servicio validando que no exista un id duplicado
    def agregar_servicio(self, servicio: Servicio):
        if any(s.id == servicio.id for s in self._servicios):
            raise DatoInvalidoError(f"Ya existe un servicio registrado con el ID '{servicio.id}'.")
        self._servicios.append(servicio)
        registrar_log("INFO", f"Servicio agregado a memoria: {servicio.obtener_resumen()}")

# Busca un servicio por su id en la lista interna
    def buscar_servicio(self, id_servicio: str) -> Servicio:
        for servicio in self._servicios:
            if servicio.id == id_servicio:
                return servicio
        raise EntidadNoEncontradaError(f"No se encontró ningún servicio con ID '{id_servicio}'.")

# Registra una reserva en la lista interna
    def agregar_reserva(self, reserva: Reserva):
        self._reservas.append(reserva)
