from dataclasses import dataclass
from typing import List, Any, Optional

from .parser import NahualParser
from .types import TipoNahual, Valor, TipoError, Lista
from .environment import Environment
from .error_handler import ErrorSemantico


class Funcion:
    pass


class NahualInterpreter:
    def __init__(self, debug=False):
        self.debug = debug
        self.parser = NahualParser(debug)
        self.entorno_global = Environment()
        self.entorno_actual = self.entorno_global
        self.stack = []
        self._inicializar_funciones_base()

    def _inicializar_funciones_base(self):
        def invocar(*args):
            print(*[str(arg) for arg in args])

        def percibir(mensaje: str = "") -> str:
            return Valor(TipoNahual.MANTRA, input(mensaje))

        def longitud(coleccion: Valor) -> Valor:
            if coleccion.tipo == TipoNahual.LISTA:
                return Valor(TipoNahual.ESPIRITU, coleccion.valor.longitud())
            elif coleccion.tipo == TipoNahual.MANTRA:
                return Valor(TipoNahual.ESPIRITU, len(coleccion.valor))
            raise TipoError(f"Tipo {coleccion.tipo} no soporta longitud")

        self.entorno_global.definir_funcion("invocar", Funcion("invocar", [], invocar, self.entorno_global))
        self.entorno_global.definir_funcion("percibir",
                                            Funcion("percibir", [("mantra", "mensaje")], percibir, self.entorno_global))
        self.entorno_global.definir_funcion("longitud", Funcion("longitud", [("generico", "coleccion")], longitud,
                                                                self.entorno_global))

    def ejecutar(self, nodo: Any) -> Valor:
        metodo = getattr(self, f'ejecutar_{nodo[0]}', None)
        if metodo:
            return metodo(*nodo[1:])
        raise NotImplementedError(f"No se puede ejecutar nodo de tipo {nodo[0]}")

    def ejecutar_programa(self, declaraciones: List) -> Valor:
        resultado = None
        for decl in declaraciones:
            resultado = self.ejecutar(decl)
        return resultado

    def ejecutar_con_entorno(self, nodo: Any, entorno: Environment) -> Valor:
        entorno_anterior = self.entorno_actual
        self.entorno_actual = entorno
        try:
            return self.ejecutar(nodo)
        finally:
            self.entorno_actual = entorno_anterior

    def ejecutar_operacion(self, op: str, izq: Any, der: Any) -> Valor:
        val_izq = self.ejecutar(izq)
        val_der = self.ejecutar(der)

        operaciones = {
            'unir': lambda x, y: Valor(x.tipo, x.valor + y.valor),
            'separar': lambda x, y: Valor(x.tipo, x.valor - y.valor),
            'multiplicar': lambda x, y: Valor(x.tipo, x.valor * y.valor),
            'dividir': lambda x, y: Valor(x.tipo, x.valor / y.valor),
            'residuo': lambda x, y: Valor(x.tipo, x.valor % y.valor),
            'igual': lambda x, y: Valor(TipoNahual.VERDAD, x.valor == y.valor),
            'mayor': lambda x, y: Valor(TipoNahual.VERDAD, x.valor > y.valor),
            'menor': lambda x, y: Valor(TipoNahual.VERDAD, x.valor < y.valor)
        }

        if op not in operaciones:
            raise ValueError(f"Operación desconocida: {op}")

        return operaciones[op](val_izq, val_der)

    def ejecutar_vision(self, condicion: Any, verdadero: Any, falso: Optional[Any]) -> Valor:
        cond_valor = self.ejecutar(condicion)
        if not isinstance(cond_valor, Valor) or cond_valor.tipo != TipoNahual.VERDAD:
            raise TipoError("La condición debe ser una verdad")

        if cond_valor.valor:
            return self.ejecutar(verdadero)
        elif falso:
            return self.ejecutar(falso)
        return None

    def ejecutar_ritual(self, condicion: Any, cuerpo: Any) -> None:
        while True:
            cond_valor = self.ejecutar(condicion)
            if not isinstance(cond_valor, Valor) or cond_valor.tipo != TipoNahual.VERDAD:
                raise TipoError("La condición debe ser una verdad")

            if not cond_valor.valor:
                break

            self.ejecutar(cuerpo)

    def ejecutar_var_declaracion(self, tipo: str, nombre: str, valor: Any) -> None:
        valor_ejecutado = self.ejecutar(valor)
        if not valor_ejecutado.es_compatible_con(Valor(TipoNahual(tipo), None)):
            raise TipoError(
                f"Tipo inválido para variable {nombre}. Se esperaba {tipo}, se recibió {valor_ejecutado.tipo}")
        self.entorno_actual.definir_variable(nombre, valor_ejecutado)

    def ejecutar_funcion_declaracion(self, nombre: str, parametros: List[tuple], cuerpo: Any) -> None:
        funcion = Funcion(nombre, parametros, cuerpo, self.entorno_actual)
        self.entorno_actual.definir_funcion(nombre, funcion)

    def ejecutar_llamada_funcion(self, nombre: str, argumentos: List[Any]) -> Valor:
        funcion = self.entorno_actual.obtener_funcion(nombre)
        argumentos_ejecutados = [self.ejecutar(arg) for arg in argumentos]
        return funcion.ejecutar(self, argumentos_ejecutados)

    def ejecutar_lista_literal(self, elementos: List[Any]) -> Valor:
        valores = [self.ejecutar(elem) for elem in elementos]
        tipo_comun = valores[0].tipo if valores else None
        if tipo_comun and all(v.tipo == tipo_comun for v in valores):
            lista = Lista(valores, tipo_comun)
        else:
            lista = Lista(valores)
        return Valor(TipoNahual.LISTA, lista)

    def ejecutar_acceso_lista(self, lista: Any, indice: Any) -> Valor:
        valor_lista = self.ejecutar(lista)
        if valor_lista.tipo != TipoNahual.LISTA:
            raise TipoError(f"No se puede acceder por índice a tipo {valor_lista.tipo}")

        valor_indice = self.ejecutar(indice)
        if valor_indice.tipo != TipoNahual.ESPIRITU:
            raise TipoError("El índice debe ser un espiritu (entero)")

        return valor_lista.valor.obtener(valor_indice.valor)

    def ejecutar_llamada_metodo(self, objeto: Any, metodo: str, args: List[Any]) -> Valor:
        valor_objeto = self.ejecutar(objeto)
        args_evaluados = [self.ejecutar(arg) for arg in args]

        if valor_objeto.tipo == TipoNahual.LISTA:
            lista = valor_objeto.valor
            if metodo == 'agregar':
                if len(args_evaluados) != 1:
                    raise ErrorSemantico("El método agregar requiere un argumento")
                lista.agregar(args_evaluados[0])
                return Valor(TipoNahual.VERDAD, True)
            elif metodo == 'longitud':
                if args_evaluados:
                    raise ErrorSemantico("El método longitud no acepta argumentos")
                return Valor(TipoNahual.ESPIRITU, lista.longitud())
            else:
                raise ErrorSemantico(f"Método {metodo} no definido para listas")

        raise ErrorSemantico(f"Tipo {valor_objeto.tipo} no soporta métodos")

    def ejecutar_expr_aritmetica(self, operador: str, izq: Any, der: Any) -> Valor:
        return self.ejecutar_operacion(operador, izq, der)

    def ejecutar_expr_logica(self, operador: str, izq: Any, der: Any) -> Valor:
        return self.ejecutar_operacion(operador, izq, der)

    def ejecutar_expr_relacional(self, operador: str, izq: Any, der: Any) -> Valor:
        return self.ejecutar_operacion(operador, izq, der)

    def ejecutar_literal(self, valor: Any) -> Valor:
        if isinstance(valor, int):
            return Valor(TipoNahual.ESPIRITU, valor)
        elif isinstance(valor, float):
            return Valor(TipoNahual.ENERGIA, valor)
        elif isinstance(valor, str):
            return Valor(TipoNahual.MANTRA, valor)
        elif isinstance(valor, bool):
            return Valor(TipoNahual.VERDAD, valor)
        else:
            raise ValueError(f"Tipo de literal desconocido: {type(valor)}")

    def ejecutar_variable(self, nombre: str) -> Valor:
        return self.entorno_actual.obtener_variable(nombre)

    def run(self, source: str) -> None:
        nodos = self.parser.parse(source)
        self.ejecutar_programa(nodos)