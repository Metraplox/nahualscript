# src/nahual/type_checker.py

from typing import Optional
from .types import TipoNahual, Valor, TipoError
from .error_handler import ErrorTipos, Ubicacion


class VerificadorTipos:
    """Sistema de verificación de tipos para NahualScript."""

    @staticmethod
    def verificar_asignacion(valor: Valor, tipo_destino: TipoNahual, ubicacion: Optional[Ubicacion] = None) -> None:
        """Verifica que un valor sea compatible con el tipo de destino."""
        if not valor.es_compatible_con(Valor(tipo_destino, None)):
            raise ErrorTipos(
                f"Tipo incompatible en asignación",
                tipo_esperado=tipo_destino.value,
                tipo_recibido=valor.tipo.value,
                ubicacion=ubicacion
            )

    @staticmethod
    def verificar_operacion(operador: str, izq: Valor, der: Valor, ubicacion: Optional[Ubicacion] = None) -> TipoNahual:
        """Verifica y retorna el tipo resultante de una operación binaria."""
        # Operaciones aritméticas
        if operador in {'unir', 'separar', 'multiplicar', 'dividir', 'residuo'}:
            if not izq.tipo in {TipoNahual.ESPIRITU, TipoNahual.ENERGIA}:
                raise ErrorTipos(
                    f"Operador {operador} requiere operandos numéricos",
                    tipo_esperado="espiritu/energia",
                    tipo_recibido=izq.tipo.value,
                    ubicacion=ubicacion
                )
            if not der.tipo in {TipoNahual.ESPIRITU, TipoNahual.ENERGIA}:
                raise ErrorTipos(
                    f"Operador {operador} requiere operandos numéricos",
                    tipo_esperado="espiritu/energia",
                    tipo_recibido=der.tipo.value,
                    ubicacion=ubicacion
                )
            # Si alguno es energia, el resultado es energia
            return TipoNahual.ENERGIA if TipoNahual.ENERGIA in {izq.tipo, der.tipo} else TipoNahual.ESPIRITU

        # Concatenación de mantras
        elif operador == 'unir' and izq.tipo == TipoNahual.MANTRA:
            if not der.tipo == TipoNahual.MANTRA:
                raise ErrorTipos(
                    f"No se puede unir mantra con {der.tipo.value}",
                    tipo_esperado="mantra",
                    tipo_recibido=der.tipo.value,
                    ubicacion=ubicacion
                )
            return TipoNahual.MANTRA

        # Operaciones lógicas
        elif operador in {'y', 'o'}:
            if not izq.tipo == TipoNahual.VERDAD:
                raise ErrorTipos(
                    f"Operador {operador} requiere operandos de tipo verdad",
                    tipo_esperado="verdad",
                    tipo_recibido=izq.tipo.value,
                    ubicacion=ubicacion
                )
            if not der.tipo == TipoNahual.VERDAD:
                raise ErrorTipos(
                    f"Operador {operador} requiere operandos de tipo verdad",
                    tipo_esperado="verdad",
                    tipo_recibido=der.tipo.value,
                    ubicacion=ubicacion
                )
            return TipoNahual.VERDAD

        # Comparaciones
        elif operador in {'igual', 'mayor', 'menor', 'mayor_igual', 'menor_igual'}:
            if not izq.es_compatible_con(der):
                raise ErrorTipos(
                    f"No se pueden comparar tipos diferentes",
                    tipo_esperado=izq.tipo.value,
                    tipo_recibido=der.tipo.value,
                    ubicacion=ubicacion
                )
            return TipoNahual.VERDAD

        raise ValueError(f"Operador desconocido: {operador}")

    @staticmethod
    def verificar_condicion(valor: Valor, ubicacion: Optional[Ubicacion] = None) -> None:
        """Verifica que un valor sea utilizable como condición."""
        if valor.tipo != TipoNahual.VERDAD:
            raise ErrorTipos(
                "La condición debe ser de tipo verdad",
                tipo_esperado="verdad",
                tipo_recibido=valor.tipo.value,
                ubicacion=ubicacion
            )

    @staticmethod
    def inferir_tipo_literal(valor: Any) -> TipoNahual:
        """Infiere el tipo de un valor literal."""
        if isinstance(valor, bool):
            return TipoNahual.VERDAD
        elif isinstance(valor, int):
            return TipoNahual.ESPIRITU
        elif isinstance(valor, float):
            return TipoNahual.ENERGIA
        elif isinstance(valor, str):
            return TipoNahual.MANTRA
        elif isinstance(valor, list):
            return TipoNahual.LISTA
        raise ValueError(f"No se puede inferir tipo para: {type(valor)}")

    @staticmethod
    def es_numerico(tipo: TipoNahual) -> bool:
        """Verifica si un tipo es numérico."""
        return tipo in {TipoNahual.ESPIRITU, TipoNahual.ENERGIA}