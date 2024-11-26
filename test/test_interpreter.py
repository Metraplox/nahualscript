from nahual.error_handler import InterpreterError
from nahual.types import TipoNahual, Valor
from nahual.interpreter import NahualInterpreter

import pytest

from src.nahual.error_handler import ErrorTipo, ErrorSintaxis
from src.nahual.types import TipoError


def test_calculadora():
    interpreter = NahualInterpreter()
    with open('examples/programas/calculadora.nhl', 'r') as f:
        source = f.read()
    interpreter.run(source)

    # Verificar resultados
    assert interpreter.entorno_global.obtener_variable('x').valor == 10
    assert interpreter.entorno_global.obtener_variable('y').valor == 5


def test_factorial():
    interpreter = NahualInterpreter()
    source = '''
    sabiduria factorial(espiritu n) {
        vision (n menor 2) {
            retornar 1;
        }
        retornar n multiplicar factorial(n separar 1);
    }
    '''
    interpreter.run(source)
    resultado = interpreter.ejecutar_llamada_funcion('factorial', [Valor(TipoNahual.ESPIRITU, 5)])
    assert resultado.valor == 120


def test_error_handling():
    interpreter = NahualInterpreter()
    with pytest.raises(TipoError):
        interpreter.run('espiritu x := "no es un número";')


def test_listas():
    interpreter = NahualInterpreter()
    source = """
    lista numeros := [1, 2, 3];
    espiritu len := longitud(numeros);
    numeros.agregar(4);
    """
    interpreter.run(source)

    numeros = interpreter.entorno_global.obtener_variable('numeros')
    assert numeros.tipo == TipoNahual.LISTA
    assert len(numeros.valor.elementos) == 4
    assert interpreter.entorno_global.obtener_variable('len').valor == 3


def test_error_tipos():
    interpreter = NahualInterpreter()
    with pytest.raises(ErrorTipo) as excinfo:
        interpreter.run('espiritu x := "no es un número";')
    assert "Tipo inválido" in str(excinfo.value)


def test_error_sintaxis():
    interpreter = NahualInterpreter()
    with pytest.raises(ErrorSintaxis) as excinfo:
        interpreter.run('espiritu x := ;')
    assert "Error de sintaxis" in str(excinfo.value)