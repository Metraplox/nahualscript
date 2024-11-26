# src/nahual/error_handler.py

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import traceback


@dataclass
class LexPosition:
    """Representa una posición en el código fuente durante el análisis léxico."""
    line: int
    column: int

    def __str__(self) -> str:
        return f"línea {self.line}, columna {self.column}"


@dataclass
class LexError:
    """Representa un error durante el análisis léxico."""
    message: str
    position: LexPosition
    severity: str = "ERROR"

    def __str__(self) -> str:
        return f"{self.severity} en {self.position}: {self.message}"


@dataclass
class Ubicacion:
    """Representa una ubicación en el código fuente."""
    linea: int
    columna: int
    archivo: str = '<desconocido>'
    contexto: Optional[str] = None

    def __str__(self) -> str:
        base = f"línea {self.linea}, columna {self.columna}"
        if self.archivo != '<desconocido>':
            base = f"{self.archivo}:{base}"
        if self.contexto:
            base += f"\n  {self.contexto}"
        return base


@dataclass
class MarcoEjecucion:
    """Representa un marco en la pila de ejecución."""
    nombre: str
    ubicacion: Ubicacion
    variables: Dict[str, Any] = None

    def __str__(self) -> str:
        resultado = f"  en {self.nombre} ({self.ubicacion})"
        if self.variables:
            vars_str = ", ".join(f"{k}={v}" for k, v in self.variables.items())
            resultado += f"\n    variables locales: {vars_str}"
        return resultado


class ErrorNahual(Exception):
    """Clase base para todos los errores de NahualScript."""

    def __init__(
            self,
            mensaje: str,
            ubicacion: Optional[Ubicacion] = None,
            pila: List[MarcoEjecucion] = None,
            sugerencia: Optional[str] = None
    ):
        self.mensaje = mensaje
        self.ubicacion = ubicacion
        self.pila = pila or []
        self.sugerencia = sugerencia
        super().__init__(self.formatear_error())

    def formatear_error(self) -> str:
        partes = [
            "🔮 Error en el Ritual Místico 🔮",
            f"📜 {self.mensaje}"
        ]

        if self.ubicacion:
            partes.append(f"📍 Ubicación: {self.ubicacion}")

        if self.pila:
            partes.append("\n🔍 Rastro del ritual:")
            for marco in reversed(self.pila):
                partes.append(str(marco))

        if self.sugerencia:
            partes.append(f"\n💫 Sugerencia mística: {self.sugerencia}")

        return "\n".join(partes)


class ErrorSintaxis(ErrorNahual):
    """Error en la estructura del código."""

    def __init__(self, mensaje: str, ubicacion: Optional[Ubicacion] = None, **kwargs):
        sugerencia = kwargs.pop('sugerencia', "Revisa la estructura de tu ritual")
        super().__init__(
            mensaje,
            ubicacion=ubicacion,
            sugerencia=sugerencia,
            **kwargs
        )


class ErrorSemantico(ErrorNahual):
    """Error en el significado o lógica del código."""
    pass


class ErrorTipos(ErrorNahual):
    """Error de tipos en el código."""

    def __init__(self, mensaje: str, tipo_esperado: str, tipo_recibido: str, **kwargs):
        super().__init__(
            mensaje,
            sugerencia=f"Se esperaba una energía de tipo {tipo_esperado}",
            **kwargs
        )
        self.tipo_esperado = tipo_esperado
        self.tipo_recibido = tipo_recibido


class ErrorEjecucion(ErrorNahual):
    """Error durante la ejecución del programa."""
    pass


def decorar_manejo_errores(metodo):
    """Decorador para manejar errores en métodos del intérprete."""

    def wrapper(self, *args, **kwargs):
        try:
            return metodo(self, *args, **kwargs)
        except ErrorNahual as e:
            if hasattr(self, 'debug') and self.debug:
                print("\nTraza completa para depuración:")
                traceback.print_exc()
            print(str(e))
            return None
        except Exception as e:
            error = ErrorEjecucion(
                f"Error inesperado: {str(e)}",
                sugerencia="Contacta a los ancianos sabios (desarrolladores)"
            )
            print(str(error))
            if hasattr(self, 'debug') and self.debug:
                traceback.print_exc()
            return None

    return wrapper


class ManejadorErrores:
    """Clase para manejar y coleccionar errores durante la ejecución."""

    def __init__(self):
        self.errores: List[ErrorNahual] = []
        self.ubicacion_actual: Optional[Ubicacion] = None
        self.pila: List[MarcoEjecucion] = []

    def registrar_error(self, error: ErrorNahual) -> None:
        """Registra un error y lo agrega a la lista de errores."""
        if not error.ubicacion:
            error.ubicacion = self.ubicacion_actual
        if not error.pila:
            error.pila = self.pila.copy()
        self.errores.append(error)

    def tiene_errores(self) -> bool:
        """Retorna True si hay errores registrados."""
        return len(self.errores) > 0

    def obtener_errores(self) -> List[str]:
        """Retorna lista de errores formateados."""
        return [str(error) for error in self.errores]

    def limpiar(self) -> None:
        """Limpia todos los errores registrados."""
        self.errores.clear()