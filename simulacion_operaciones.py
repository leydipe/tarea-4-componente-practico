"""Pruebas de las operaciones del sistema Software FJ"""

import re
import sys
from pathlib import Path


# ruta donde se encuentran los archivos del proyecto

RUTA_SRC = Path(__file__).resolve().parent / "tarea-4-componente-practico" / "src"

if not RUTA_SRC.is_dir():
    raise FileNotFoundError(f"No se encontró la carpeta de módulos: {RUTA_SRC}")

sys.path.insert(0, str(RUTA_SRC))

from cliente import Cliente
from excepciones import ClienteInvalidoError, ErrorSoftwareFJ
from registro_logs import logger
from servicios import AlquilerEquipo, AsesoriaEspecializada, SalaReserva


def validar_cliente(identificacion, nombre, correo, telefono):
    
    """revisa que los datos del cliente sean correctos"""

    if not isinstance(identificacion, str) or not identificacion.strip():
        raise ClienteInvalidoError("la identificación es obligatoria")

    if not isinstance(nombre, str) or not nombre.strip():
        raise ClienteInvalidoError("el nombre es obligatorio")

    if not nombre.strip().replace(" ", "").isalpha():
        raise ClienteInvalidoError(
            "el nombre solo debe contener letras y espacios"
        )

    patron_correo = r"[^@\s]+@[^@\s.]+(?:\.[^@\s.]+)+"
    if not isinstance(correo, str) or not re.fullmatch(
        patron_correo, correo.strip()
    ):
        raise ClienteInvalidoError("el correo no tiene un formato válido")

    if not isinstance(telefono, str) or not re.fullmatch(
        r"\d{10}", telefono.strip()
    ):
        raise ClienteInvalidoError(
            "el teléfono debe tener exactamente 10 dígitos"
        )


def crear_cliente(identificacion, nombre, correo, telefono):
    """valida los datos y crea el cliente"""

    validar_cliente(identificacion, nombre, correo, telefono)
    cliente = Cliente(identificacion, nombre, correo, telefono)
    return f"cliente creado: {cliente.obtener_nombre()}"


def ejecutar_operacion(numero, descripcion, accion):
    """ejecuta cada operación y registra los errores que encuentre"""

    print(f"\n--- Operación {numero}: {descripcion} ---")

    try:
        resultado = accion()
    except (ErrorSoftwareFJ, TypeError, ValueError) as error:
        logger.excepcion(
            error,
            origen=f"SimulaciónOperaciones.operacion_{numero}",
        )
        print(f"Operación fallida: {error}")
    else:
        print(f"Operación exitosa: {resultado}")


def crear_sala_y_calcular_costo():

    """crea una sala y calcula el costo de su reserva"""

    sala = SalaReserva(
        "S001",
        "Sala de reuniones",
        "Sala para reuniones empresariales",
        50000,
        1,
    )
    total = sala.calcular_costo(2)
    return f"{sala}; costo por 2 horas con impuesto: ${total:,.2f}"


def crear_equipo_y_calcular_costo():

    """crea un equipo y calcula el costo del alquiler"""

    equipo = AlquilerEquipo(
        "E001",
        "Proyector",
        "Proyector para presentaciones",
        25000,
        1,
    )
    total = equipo.calcular_costo(2)
    return f"{equipo}; costo por 2 unidades con impuesto: ${total:,.2f}"


def crear_asesoria_y_calcular_costo():

    """crea una asesoría y calcula el costo del servicio"""

    asesoria = AsesoriaEspecializada(
        "A001",
        "Asesoría informática",
        "Orientación técnica especializada",
        80000,
        1,
        "avanzado",
    )
    total = asesoria.calcular_costo(1.5)
    return f"{asesoria}; costo por 1.5 horas con impuesto: ${total:,.2f}"


def crear_servicio_invalido():
    """prueba qué pasa cuando la tarifa es negativa"""

    # se usa una tarifa negativa para probar la validación

    SalaReserva(
        "S002",
        "Sala inválida",
        "Prueba de tarifa incorrecta",
        -5000,
        1,
    )
    return "este resultado no debería alcanzarse ya que la tarifa es negativa"


def calcular_equipo_con_cantidad_invalida():

    """comprueba que no se pueda calcular con cantidad cero"""

    equipo = AlquilerEquipo(
        "E002",
        "Micrófono",
        "Micrófono para eventos",
        10000,
        1,
    )
    # se coloca cero para comprobar que el sistema lo rechace

    return equipo.calcular_costo(0)


def main():

    """ejecuta todas las pruebas del programa"""

    operaciones = [
        (
            "crear un cliente-válido",
            lambda: crear_cliente(
                "1001", "Ana Pérez", "ana@ejemplo.com", "3001234567"
            ),
        ),
        (
            "rechazar una identificación vacía",
            lambda: crear_cliente(
                " ", "Ana Pérez", "ana@ejemplo.com", "3001234567"
            ),
        ),
        (
            "rechazar un nombre con números",
            lambda: crear_cliente(
                "1002", "Ana123", "ana@ejemplo.com", "3001234567"
            ),
        ),
        (
            "rechazar un correo con formato incorrecto",
            lambda: crear_cliente(
                "1003", "Luis Gómez", "correo-invalido", "3001234567"
            ),
        ),
        (
            "rechazar un teléfono que no tiene 10 dígitos",
            lambda: crear_cliente(
                "1004", "Sara Ruiz", "sara@ejemplo.com", "12345"
            ),
        ),
        (
            "crear una sala y calcular su costo",
            crear_sala_y_calcular_costo,
        ),
        (
            "crear un alquiler de equipo y calcular su costo",
            crear_equipo_y_calcular_costo,
        ),
        (
            "crear una asesoría y calcular su costo",
            crear_asesoria_y_calcular_costo,
        ),
        (
            "rechazar un servicio con tarifa negativa",
            crear_servicio_invalido,
        ),
        (
            "rechazar el cálculo de un equipo con cantidad cero",
            calcular_equipo_con_cantidad_invalida,
        ),
    ]

    # recorre la lista y ejecuta cada prueba

    for numero, (descripcion, accion) in enumerate(operaciones, start=1):
        ejecutar_operacion(numero, descripcion, accion)

    print("\nSimulación finalizada.:)")


if __name__ == "__main__":
    main()