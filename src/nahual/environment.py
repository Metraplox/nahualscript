from .types import Valor

class Environment:
    def __init__(self, parent=None):
        self.variables: Dict[str, Valor] = {}
        self.funciones: Dict[str, 'Funcion'] = {}
        self.parent = parent

    def definir_variable(self, nombre: str, valor: Valor) -> None:
        self.variables[nombre] = valor

    def definir_funcion(self, nombre: str, funcion: 'Funcion') -> None:
        self.funciones[nombre] = funcion

    def obtener_variable(self, nombre: str) -> Valor:
        if nombre in self.variables:
            return self.variables[nombre]
        if self.parent:
            return self.parent.obtener_variable(nombre)
        raise NameError(f"Variable no definida: {nombre}")

    def obtener_funcion(self, nombre: str) -> 'Funcion':
        if nombre in self.funciones:
            return self.funciones[nombre]
        if self.parent:
            return self.parent.obtener_funcion(nombre)
        raise NameError(f"Función no definida: {nombre}")