"""Sistema de logs - Software FJ.

Escribe automáticamente eventos y errores en un archivo de texto
(sin bases de datos). Uso rápido desde cualquier módulo del proyecto:

    from registro_logs import logger, registrar_errores

    logger.evento("Cliente registrado: Ana", origen="Cliente")
    logger.excepcion(error, origen="Reserva.confirmar")

El logger NUNCA debe tumbar la aplicación: si no puede escribir en el
archivo, avisa por consola y el programa sigue funcionando.
"""

import os
import sys
import traceback
from datetime import datetime
from functools import wraps

from excepciones import ErrorSoftwareFJ

ARCHIVO_LOG_POR_DEFECTO = "logs/software_fj.log"


class RegistroLogs:
    """Escribe líneas: fecha | nivel | origen | mensaje."""

    NIVELES = ("DEBUG", "INFO", "AUDIT", "WARNING", "ERROR", "CRITICAL")

    def __init__(self, archivo=ARCHIVO_LOG_POR_DEFECTO):
        self.archivo = archivo
        try:
            carpeta = os.path.dirname(archivo)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)
        except OSError as exc:
            print(f"[LOG] No se pudo crear la carpeta de logs: {exc}", file=sys.stderr)

    # -- escritura base ------------------------------------------------------
    def escribir(self, nivel, mensaje, origen="app"):
        nivel = str(nivel).upper()
        if nivel not in self.NIVELES:
            nivel = "WARNING"
            mensaje = f"(nivel de log desconocido) {mensaje}"
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"{fecha} | {nivel:<8} | {origen} | {mensaje}"
        try:
            # "a" = append: nunca borra lo que ya estaba escrito
            with open(self.archivo, "a", encoding="utf-8") as f:
                f.write(linea + "\n")
        except OSError as exc:
            # Estabilidad: si falla el archivo, el programa continúa
            print(f"[LOG] No se pudo escribir en el archivo ({exc}): {linea}", file=sys.stderr)

    # -- atajos por nivel ----------------------------------------------------
    def debug(self, mensaje, origen="app"):
        self.escribir("DEBUG", mensaje, origen)

    def info(self, mensaje, origen="app"):
        self.escribir("INFO", mensaje, origen)

    def evento(self, mensaje, origen="app"):
        """Alias de info(): para eventos normales (registro, reserva, etc.)."""
        self.escribir("INFO", mensaje, origen)

    def audit(self, mensaje, origen="app"):
        """Trazabilidad: cierre de procesos, cambios de estado, etc."""
        self.escribir("AUDIT", mensaje, origen)

    def warning(self, mensaje, origen="app"):
        self.escribir("WARNING", mensaje, origen)

    def error(self, mensaje, origen="app"):
        self.escribir("ERROR", mensaje, origen)

    def critical(self, mensaje, origen="app"):
        self.escribir("CRITICAL", mensaje, origen)

    # -- excepciones ---------------------------------------------------------
    def excepcion(self, exc, origen="app", nivel="ERROR", con_traza=True):
        """Registra una excepción y toda su cadena de causas.

        Si la excepción fue lanzada con `raise X from Y`, también se
        escribe Y (encadenamiento de excepciones).
        """
        etiqueta = "" if isinstance(exc, ErrorSoftwareFJ) else "(estándar) "
        self.escribir(nivel, f"{etiqueta}{type(exc).__name__}: {exc}", origen)

        causa = exc.__cause__ or (None if exc.__suppress_context__ else exc.__context__)
        profundidad = 1
        while causa is not None and profundidad <= 10:
            self.escribir(nivel, f"  causada por -> {type(causa).__name__}: {causa}", origen)
            causa = causa.__cause__
            profundidad += 1

        if con_traza and exc.__traceback__ is not None:
            traza = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            self.escribir("DEBUG", "Traza: " + traza.strip().replace("\n", " || "), origen)


# Instancia lista para importar y compartir en todo el proyecto
logger = RegistroLogs()


def registrar_errores(log=None, relanzar=True, valor_por_defecto=None):
    """Decorador: registra en el log cualquier excepción de la función.

    relanzar=True  -> registra y vuelve a lanzar el error (lo maneja quien llama).
    relanzar=False -> registra y devuelve `valor_por_defecto` (el programa sigue).
    """

    def decorador(func):
        @wraps(func)
        def envoltura(*args, **kwargs):
            destino = log or logger
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                destino.excepcion(exc, origen=func.__qualname__)
                if relanzar:
                    raise
                return valor_por_defecto

        return envoltura

    return decorador
