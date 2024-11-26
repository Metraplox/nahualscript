from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Union, Optional


class TipoNahual(Enum):
    ESPIRITU = 'espiritu'  # Enteros
    ENERGIA = 'energia'  # Flotantes
    MANTRA = 'mantra'  # Strings
    VERDAD = 'verdad'  # Booleanos
    LISTA = 'lista'  # Lista de valores
    MAPA = 'mapa'  # Diccionario/Mapa


@dataclass
class Lista:
    elementos: List['Valor']
    tipo_elementos: Optional[TipoNahual] = None  # Para listas tipadas

    def agregar(self, valor: 'Valor') -> None:
        if self.tipo_elementos and valor.tipo != self.tipo_elementos:
            raise TipoError(f"No se puede agregar {valor.tipo} a lista de {self.tipo_elementos}")
        self.elementos.append(valor)

    def obtener(self, indice: int) -> 'Valor':
        if not (0 <= indice < len(self.elementos)):
            raise IndexError(f"Índice {indice} fuera de rango")
        return self.elementos[indice]

    def longitud(self) -> int:
        return len(self.elementos)


@dataclass
class Valor:
    tipo: TipoNahual
    valor: Any
    posicion: Optional['Posicion'] = None  # Para rastreo de errores

    def __str__(self):
        if self.tipo == TipoNahual.LISTA:
            return f"[{', '.join(str(x) for x in self.valor.elementos)}]"
        return str(self.valor)

    def es_compatible_con(self, otro: 'Valor') -> bool:
        if self.tipo == otro.tipo:
            return True
        # Permitir coerción entre ESPIRITU y ENERGIA
        if {self.tipo, otro.tipo} == {TipoNahual.ESPIRITU, TipoNahual.ENERGIA}:
            return True
        return False

    def comparar_con(self, otro: 'Valor', operador: str) -> 'Valor':
        """Realiza una comparación entre valores."""
        if not self.es_compatible_con(otro):
            raise TipoError(f"No se pueden comparar valores de tipo {self.tipo} y {otro.tipo}")

        resultado = False
        if operador == 'mayor':
            resultado = self.valor > otro.valor
        elif operador == 'menor':
            resultado = self.valor < otro.valor
        elif operador == 'igual':
            resultado = self.valor == otro.valor

        return Valor(TipoNahual.VERDAD, resultado)

    def convertir_a(self, tipo_destino: TipoNahual) -> 'Valor':
        """Intenta convertir el valor a otro tipo"""
        if self.tipo == tipo_destino:
            return self

        conversiones = {
            (TipoNahual.ESPIRITU, TipoNahual.ENERGIA): lambda x: float(x),
            (TipoNahual.ENERGIA, TipoNahual.ESPIRITU): lambda x: int(x),
            (TipoNahual.ESPIRITU, TipoNahual.MANTRA): lambda x: str(x),
            (TipoNahual.ENERGIA, TipoNahual.MANTRA): lambda x: str(x),
            (TipoNahual.MANTRA, TipoNahual.ESPIRITU): lambda x: int(x),
            (TipoNahual.MANTRA, TipoNahual.ENERGIA): lambda x: float(x),
        }

        try:
            conversion = conversiones.get((self.tipo, tipo_destino))
            if conversion:
                return Valor(tipo_destino, conversion(self.valor))
            raise TipoError(f"No se puede convertir de {self.tipo} a {tipo_destino}")
        except (ValueError, TypeError) as e:
            raise TipoError(f"Error al convertir valor: {e}")


class TipoError(Exception):
    def __init__(self, mensaje: str, valor: Optional[Valor] = None):
        self.mensaje = mensaje
        self.valor = valor
        self.posicion = valor.posicion if valor else None

    def __str__(self):
        if self.posicion:
            return f"Error de tipo en {self.posicion}: {self.mensaje}"
        return f"Error de tipo: {self.mensaje}"
