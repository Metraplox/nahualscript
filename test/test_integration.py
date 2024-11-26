import pytest
from nahual.interpreter import NahualInterpreter

def test_fibonacci():
    interpreter = NahualInterpreter(debug=True)
    source = """
    sabiduria fibonacci(espiritu n) {
        vision(n menor 2) {
            retornar n;
        }
        retornar fibonacci(n separar 1) unir fibonacci(n separar 2);
    }
    """
    interpreter.run(source)
    result = interpreter.execute(('llamada_funcion', 'fibonacci', [10]))
    assert result.valor == 55