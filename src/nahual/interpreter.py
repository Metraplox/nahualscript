# src/nahual/interpreter.py

from typing import Any, List, Optional, Dict
from .types import TipoNahual, Valor, TipoError, Lista
from .environment import Environment
from .error_handler import (
    ErrorNahual, ErrorSemantico, ErrorTipos, ErrorEjecucion,
    Ubicacion, MarcoEjecucion, decorar_manejo_errores, ManejadorErrores
)


class NahualInterpreter:
    """Intérprete principal para NahualScript."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.entorno_global = Environment()
        self.entorno_actual = self.entorno_global
        self.manejador_errores = ManejadorErrores()
        self._inicializar_funciones_base()

    def _inicializar_funciones_base(self):
        """Inicializa las funciones nativas del lenguaje."""

        def invocar(*args) -> None:
            """Función para imprimir valores."""
            print(*[str(arg.valor) for arg in args])

        def percibir(mensaje: str = "") -> Valor:
            """Función para recibir entrada del usuario."""
            try:
                valor = input(mensaje)
                return Valor(TipoNahual.MANTRA, valor)
            except Exception as e:
                raise ErrorEjecucion(
                    "Error al leer entrada",
                    sugerencia="Verifica que la entrada sea válida"
                )

        def convertir(valor: Valor, tipo_destino: str) -> Valor:
            """Función para convertir un valor a un tipo específico."""
            try:
                tipo_destino_obj = TipoNahual(tipo_destino)
                return valor.convertir_a(tipo_destino_obj)
            except TipoError as e:
                raise ErrorTipos(
                    f"No se puede convertir {valor.tipo.value} a {tipo_destino}",
                    tipo_esperado=tipo_destino,
                    tipo_recibido=valor.tipo.value
                )
            except ValueError:
                raise ErrorSemantico(f"Tipo desconocido: {tipo_destino}")

        def longitud(coleccion: Valor) -> Valor:
            """Calcula la longitud de una colección (lista o cadena)."""
            if coleccion.tipo == TipoNahual.LISTA:
                return Valor(TipoNahual.ESPIRITU, len(coleccion.valor))
            elif coleccion.tipo == TipoNahual.MANTRA:
                return Valor(TipoNahual.ESPIRITU, len(coleccion.valor))
            raise TipoError(f"Tipo {coleccion.tipo} no soporta longitud")

        # Registrar funciones nativas en el entorno global
        self._registrar_funcion_nativa("invocar", invocar)
        self._registrar_funcion_nativa("percibir", percibir)
        self._registrar_funcion_nativa("convertir", convertir)
        self._registrar_funcion_nativa("longitud", longitud)

    def _registrar_funcion_nativa(self, nombre: str, funcion: Any) -> None:
        """Registra una función nativa en el entorno global."""
        self.entorno_global.definir_funcion(nombre, funcion)

    def ejecutar(self, nodo: Any) -> Optional[Valor]:
        """Ejecuta un nodo del AST."""
        if nodo is None:
            return None

        if isinstance(nodo, tuple):
            tipo_nodo = nodo[0]
            if tipo_nodo == 'bloque':
                return self.ejecutar_bloque(nodo[1], nodo[2] if len(nodo) > 2 else None)
            elif tipo_nodo == 'variable':
                return self.entorno_actual.obtener_variable(nodo[1])
            metodo = getattr(self, f'ejecutar_{tipo_nodo}', None)
            if metodo:
                return metodo(*nodo[1:])
            raise NotImplementedError(f"No se puede ejecutar nodo de tipo {tipo_nodo}")

        return nodo

    @decorar_manejo_errores
    def ejecutar_programa(self, nodo: Any) -> Valor:
        """Ejecuta un nodo de tipo 'programa'."""
        declaraciones = nodo[1]  # Extrae las declaraciones del nodo
        resultado = None
        for declaracion in declaraciones:
            resultado = self.ejecutar(declaracion)
        return resultado

    @decorar_manejo_errores
    def ejecutar_var_declaracion(self, tipo: str, nombre: str, valor: Any, ubicacion: Optional[dict] = None) -> None:
        """Ejecuta una declaración de variable."""
        if isinstance(valor, str) and valor == 'percibir':
            try:
                entrada = input()
                if tipo == 'energia':
                    valor_ejecutado = Valor(TipoNahual.ENERGIA, float(entrada))
                elif tipo == 'espiritu':
                    valor_ejecutado = Valor(TipoNahual.ESPIRITU, int(entrada))
                else:
                    valor_ejecutado = Valor(TipoNahual.MANTRA, entrada)
            except ValueError:
                raise ErrorTipos(
                    f"No se puede convertir la entrada a {tipo}",
                    tipo_esperado=tipo,
                    tipo_recibido="entrada inválida"
                )
        else:
            valor_ejecutado = self.ejecutar(valor)
            if not valor_ejecutado:
                return None

        try:
            tipo_nahual = TipoNahual(tipo)
            if not valor_ejecutado.es_compatible_con(Valor(tipo_nahual, None)):
                raise ErrorTipos(
                    f"Tipo incompatible en asignación a '{nombre}'",
                    tipo_esperado=tipo,
                    tipo_recibido=valor_ejecutado.tipo.value
                )
            self.entorno_actual.definir_variable(nombre, valor_ejecutado)
        except ValueError:
            raise ErrorSemantico(f"Tipo desconocido: {tipo}")
    @decorar_manejo_errores
    def ejecutar_funcion_declaracion(self, nombre: str, parametros: List[tuple], cuerpo: Any,
                                     ubicacion: Optional[dict]) -> None:
        """Ejecuta una declaración de función."""
        funcion = {
            'parametros': parametros,
            'cuerpo': cuerpo,
            'entorno': self.entorno_actual,
            'ubicacion': ubicacion  # Guarda la ubicación para rastreo de errores
        }
        self.entorno_actual.definir_funcion(nombre, funcion)

    @decorar_manejo_errores
    def ejecutar_llamada_funcion(self, nombre: str, argumentos: List[Any], ubicacion: Optional[dict] = None) -> \
    Optional[Valor]:
        """
        Executes a function call by resolving its name and evaluating arguments.
        """
        try:
            funcion = self.entorno_actual.obtener_funcion(nombre)
            args_evaluados = [self.ejecutar(arg) for arg in argumentos]

            if None in args_evaluados:
                return None

            nuevo_entorno = Environment(funcion['entorno'])
            for (tipo, param_nombre), arg in zip(funcion['parametros'], args_evaluados):
                if not arg.es_compatible_con(Valor(TipoNahual(tipo), None)):
                    raise ErrorTipos(
                        f"Argumento inválido para parámetro '{param_nombre}'",
                        tipo_esperado=tipo,
                        tipo_recibido=arg.tipo.value
                    )
                nuevo_entorno.definir_variable(param_nombre, arg)

            return self.ejecutar_con_entorno(funcion['cuerpo'], nuevo_entorno)
        except KeyError:
            raise ErrorSemantico(f"Función no definida: {nombre}")
        except Exception as e:
            raise ErrorEjecucion(
                f"Error al ejecutar la función '{nombre}': {str(e)}",
                sugerencia="Revisa la definición de la función y los argumentos proporcionados"
            )

    def ejecutar_operacion(self, op: str, izq: Any, der: Any, ubicacion: Optional[dict] = None) -> Optional[Valor]:
        """Ejecuta una operación binaria."""
        val_izq = self.ejecutar(izq)
        if val_izq is None:
            return None

        val_der = self.ejecutar(der)
        if val_der is None:
            return None

        try:
            # Operaciones numéricas
            if op == 'unir':
                # Solo para números
                if val_izq.tipo in {TipoNahual.ESPIRITU, TipoNahual.ENERGIA} and val_der.tipo in {TipoNahual.ESPIRITU,
                                                                                                  TipoNahual.ENERGIA}:
                    resultado = val_izq.valor + val_der.valor
                    tipo_resultado = TipoNahual.ENERGIA if TipoNahual.ENERGIA in {val_izq.tipo,
                                                                                  val_der.tipo} else TipoNahual.ESPIRITU
                    return Valor(tipo_resultado, resultado)
                raise TipoError(f"Operación unir solo admite valores numéricos (ESPIRITU o ENERGIA)")

            # Otras operaciones
            elif op == 'separar':
                resultado = val_izq.valor - val_der.valor
                tipo_resultado = TipoNahual.ENERGIA if TipoNahual.ENERGIA in {val_izq.tipo,
                                                                              val_der.tipo} else TipoNahual.ESPIRITU
                return Valor(tipo_resultado, resultado)
            elif op == 'multiplicar':
                resultado = val_izq.valor * val_der.valor
                tipo_resultado = TipoNahual.ENERGIA if TipoNahual.ENERGIA in {val_izq.tipo,
                                                                              val_der.tipo} else TipoNahual.ESPIRITU
                return Valor(tipo_resultado, resultado)
            elif op == 'dividir':
                if val_der.valor == 0:
                    raise ErrorEjecucion("División por cero")
                resultado = val_izq.valor / val_der.valor
                tipo_resultado = TipoNahual.ENERGIA
                return Valor(tipo_resultado, resultado)
            elif op == 'residuo':
                resultado = val_izq.valor % val_der.valor
                tipo_resultado = TipoNahual.ESPIRITU
                return Valor(tipo_resultado, resultado)

            # Operaciones de comparación
            elif op in ['mayor', 'menor', 'igual']:
                if not val_izq.es_compatible_con(val_der):
                    raise TipoError(f"No se pueden comparar valores de tipo {val_izq.tipo} y {val_der.tipo}")

                if op == 'mayor':
                    resultado = val_izq.valor > val_der.valor
                elif op == 'menor':
                    resultado = val_izq.valor < val_der.valor
                else:  # igual
                    resultado = val_izq.valor == val_der.valor

                return Valor(TipoNahual.VERDAD, resultado)

            raise ValueError(f"Operador no soportado: {op}")

        except Exception as e:
            raise ErrorEjecucion(f"Error en operación {op}: {str(e)}", ubicacion)

    def ejecutar_ritual(self, condicion: Any, cuerpo: Any, ubicacion: Optional[dict] = None) -> None:
        """
        Ejecuta un ciclo `ritual` (equivalente a un `mientras`).
        """
        while True:
            cond_valor = self.ejecutar(condicion)
            if not isinstance(cond_valor, Valor) or cond_valor.tipo != TipoNahual.VERDAD:
                raise TipoError("La condición debe ser una verdad")

            if not cond_valor.valor:
                break

            self.ejecutar(cuerpo)

    def ejecutar_vision(self, condicion: Any, verdadero: Any, falso: Any, ubicacion: Optional[dict] = None) -> Optional[
        Valor]:
        """Ejecuta una declaración vision (if-else)."""
        try:
            cond_valor = self.ejecutar(condicion)
            if cond_valor is None:
                return None

            if cond_valor.tipo != TipoNahual.VERDAD:
                raise TipoError("La condición debe ser una verdad")

            if cond_valor.valor:
                return self.ejecutar(verdadero)
            elif falso:
                return self.ejecutar(falso)
            return None
        except Exception as e:
            raise ErrorEjecucion(f"Error en evaluación de visión: {str(e)}", ubicacion)

    def convertir_a_tipo(self, valor: Valor, tipo_destino: TipoNahual) -> Valor:
        """Convierte un valor al tipo especificado."""
        try:
            if tipo_destino == TipoNahual.ENERGIA:
                return Valor(TipoNahual.ENERGIA, float(valor.valor))
            elif tipo_destino == TipoNahual.ESPIRITU:
                return Valor(TipoNahual.ESPIRITU, int(float(valor.valor)))
            elif tipo_destino == TipoNahual.MANTRA:
                return Valor(TipoNahual.MANTRA, str(valor.valor))
            elif tipo_destino == TipoNahual.VERDAD:
                return Valor(TipoNahual.VERDAD, bool(valor.valor))
            raise TipoError(f"No se puede convertir a tipo {tipo_destino}")
        except Exception as e:
            raise TipoError(f"Error en conversión: {str(e)}")

    def _aplicar_operacion(self, op: str, izq: Valor, der: Valor) -> Optional[Valor]:
        """Aplica una operación binaria a dos valores."""
        operaciones = {
            'unir': lambda x, y: x.valor + y.valor,
            'separar': lambda x, y: x.valor - y.valor,
            'multiplicar': lambda x, y: x.valor * y.valor,
            'dividir': lambda x, y: x.valor / y.valor,
            'residuo': lambda x, y: x.valor % y.valor,
            'igual': lambda x, y: x.valor == y.valor,
            'mayor': lambda x, y: x.valor > y.valor,
            'menor': lambda x, y: x.valor < y.valor,
        }

        if op not in operaciones:
            raise ValueError(f"Operador no soportado: {op}")

        # Verificar compatibilidad de tipos
        if not izq.es_compatible_con(der):
            raise ErrorTipos(
                "Tipos incompatibles en operación",
                tipo_esperado=izq.tipo.value,
                tipo_recibido=der.tipo.value
            )

        try:
            resultado = operaciones[op](izq, der)
            # Determinar el tipo de retorno
            if op in {'igual', 'mayor', 'menor'}:
                return Valor(TipoNahual.VERDAD, resultado)
            return Valor(izq.tipo, resultado)
        except ZeroDivisionError:
            raise ErrorEjecucion("División por cero")
        except Exception as e:
            raise ErrorEjecucion(f"Error en operación {op}: {str(e)}")

    def ejecutar_con_entorno(self, nodo: Any, entorno: Environment) -> Optional[Valor]:
        """Ejecuta un nodo en un entorno específico."""
        entorno_anterior = self.entorno_actual
        self.entorno_actual = entorno
        try:
            return self.ejecutar(nodo)
        finally:
            self.entorno_actual = entorno_anterior

    @decorar_manejo_errores
    def run(self, source: str) -> None:
        try:
            from .parser import NahualParser
            parser = NahualParser(self.debug)
            nodos = parser.parse(source)
            if nodos:
                self.ejecutar_programa(nodos)
        except Exception as e:
            raise ErrorEjecucion(
                f"Error al ejecutar el programa: {str(e)}",
                sugerencia="Verifica que el código fuente sea válido"
            )

    def _rastrear_ubicacion(self, nodo: Any):
        """Contexto para rastrear la ubicación actual en el código."""
        from contextlib import contextmanager

        @contextmanager
        def context():
            ubicacion_anterior = self.manejador_errores.ubicacion_actual
            if len(nodo) > 2 and isinstance(nodo[2], dict) and 'linea' in nodo[2]:
                self.manejador_errores.ubicacion_actual = Ubicacion(
                    nodo[2]['linea'],
                    nodo[2]['columna']
                )
            try:
                yield
            finally:
                self.manejador_errores.ubicacion_actual = ubicacion_anterior

        return context()

    def ejecutar_literal(self, valor, ubicacion=None):
        """
        Executes a literal node and returns its corresponding value.
        """
        if isinstance(valor, tuple):
            if valor[0] == 'llamada_funcion':
                # Pass the location to handle debugging correctly
                return self.ejecutar_llamada_funcion(*valor[1:], ubicacion=ubicacion)
            raise ValueError(f"Tipo de literal inesperado con contenido: {valor}")
        elif isinstance(valor, int):
            return Valor(TipoNahual.ESPIRITU, valor)
        elif isinstance(valor, float):
            return Valor(TipoNahual.ENERGIA, valor)
        elif isinstance(valor, str):
            return Valor(TipoNahual.MANTRA, valor)
        elif isinstance(valor, bool):
            return Valor(TipoNahual.VERDAD, valor)
        else:
            raise ValueError(f"Tipo de literal desconocido: {type(valor)}")

    def ejecutar_expresion_stmt(self, expresion, ubicacion):
        """
        Ejecuta un nodo de tipo expresion_stmt.
        """
        # Ejecuta la expresión contenida en el nodo
        self.ejecutar(expresion)

    def ejecutar_bloque(self, declaraciones: list, ubicacion: Optional[dict] = None) -> None:
        """
        Ejecuta un bloque de código.

        Args:
            declaraciones: Lista de declaraciones a ejecutar
            ubicacion: Ubicación del bloque en el código
        """
        for declaracion in declaraciones:
            self.ejecutar(declaracion)

    def ejecutar_llamada_sistema(self, tipo: str, argumentos: List[Any], ubicacion: Optional[dict] = None) -> Optional[
        Valor]:
        """Ejecuta una llamada al sistema como 'invocar' o 'percibir'."""
        try:
            valores_evaluados = []
            for arg in argumentos:
                valor = self.ejecutar(arg)
                if valor is None:
                    return None
                valores_evaluados.append(valor.valor)

            if tipo == 'invocar':
                print(*valores_evaluados)
                return Valor(TipoNahual.VERDAD, True)
            elif tipo == 'percibir':
                mensaje = str(valores_evaluados[0]) if valores_evaluados else ""
                entrada = input(mensaje)
                return Valor(TipoNahual.MANTRA, entrada)
            else:
                raise ErrorSemantico(f"Función del sistema desconocida: {tipo}")
        except Exception as e:
            raise ErrorEjecucion(f"Error al ejecutar función del sistema: {str(e)}", ubicacion)
