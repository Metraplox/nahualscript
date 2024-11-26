# test/test_suite.py

import pytest
from pathlib import Path
from nahual.interpreter import NahualInterpreter
from nahual.types import TipoNahual, Valor
from nahual.error_handler import ErrorNahual, ErrorTipos, ErrorSintaxis, ErrorSemantico


class TestNahualScript:
    """Suite de pruebas completa para NahualScript."""

    @pytest.fixture
    def interpreter(self):
        """Fixture que provee un intérprete limpio para cada prueba."""
        return NahualInterpreter(debug=True)

    def test_tipos_basicos(self, interpreter):
        """Prueba la declaración y manejo de tipos básicos."""
        codigo = """
        espiritu numero := 42;
        energia decimal := 3.14;
        mantra texto := "hola mundo";
        verdad booleano := cierto;
        """
        interpreter.run(codigo)

        assert interpreter.entorno_global.obtener_variable('numero').valor == 42
        assert interpreter.entorno_global.obtener_variable('decimal').valor == 3.14
        assert interpreter.entorno_global.obtener_variable('texto').valor == "hola mundo"
        assert interpreter.entorno_global.obtener_variable('booleano').valor is True

    def test_operaciones_aritmeticas(self, interpreter):
        """Prueba las operaciones aritméticas básicas."""
        codigo = """
        espiritu a := 10;
        espiritu b := 5;
        espiritu suma := a unir b;
        espiritu resta := a separar b;
        espiritu mult := a multiplicar b;
        espiritu div := a dividir b;
        """
        interpreter.run(codigo)

        assert interpreter.entorno_global.obtener_variable('suma').valor == 15
        assert interpreter.entorno_global.obtener_variable('resta').valor == 5
        assert interpreter.entorno_global.obtener_variable('mult').valor == 50
        assert interpreter.entorno_global.obtener_variable('div').valor == 2

    def test_control_flujo(self, interpreter):
        """Prueba las estructuras de control de flujo."""
        codigo = """
        espiritu resultado := 0;
        espiritu i := 0;

        ritual(i menor 5) {
            resultado := resultado unir i;
            i := i unir 1;
        }
        """
        interpreter.run(codigo)
        assert interpreter.entorno_global.obtener_variable('resultado').valor == 10

    def test_funciones(self, interpreter):
        """Prueba la definición y llamada de funciones."""
        codigo = """
        sabiduria factorial(espiritu n) {
            vision(n menor 2) {
                retornar 1;
            }
            retornar n multiplicar factorial(n separar 1);
        }

        espiritu resultado := factorial(5);
        """
        interpreter.run(codigo)
        assert interpreter.entorno_global.obtener_variable('resultado').valor == 120

    def test_manejo_errores_tipos(self, interpreter):
        """Prueba el manejo de errores de tipos."""
        with pytest.raises(ErrorTipos) as excinfo:
            interpreter.run('espiritu x := "no es un número";')
        assert "Tipo incompatible" in str(excinfo.value)

    def test_manejo_errores_sintaxis(self, interpreter):
        """Prueba el manejo de errores de sintaxis."""
        with pytest.raises(ErrorSintaxis) as excinfo:
            interpreter.run('espiritu x := ;')
        assert "Error de sintaxis" in str(excinfo.value)

    def test_alcance_variables(self, interpreter):
        """Prueba el alcance de variables en diferentes contextos."""
        codigo = """
        espiritu global := 1;

        sabiduria prueba_alcance() {
            espiritu local := 2;
            retornar global unir local;
        }

        espiritu resultado := prueba_alcance();
        """
        interpreter.run(codigo)
        assert interpreter.entorno_global.obtener_variable('resultado').valor == 3

    def test_recursion(self, interpreter):
        """Prueba funciones recursivas."""
        codigo = """
        sabiduria fibonacci(espiritu n) {
            vision(n menor 2) {
                retornar n;
            }
            retornar fibonacci(n separar 1) unir fibonacci(n separar 2);
        }

        espiritu resultado := fibonacci(6);
        """
        interpreter.run(codigo)
        assert interpreter.entorno_global.obtener_variable('resultado').valor == 8

    def test_funciones_nativas(self, interpreter):
        """Prueba las funciones nativas del lenguaje."""
        codigo = """
        mantra entrada := percibir("Test");
        invocar entrada;
        """
        # Simular entrada del usuario
        import builtins
        original_input = builtins.input
        builtins.input = lambda _: "entrada simulada"

        try:
            interpreter.run(codigo)
            valor = interpreter.entorno_global.obtener_variable('entrada')
            assert valor.tipo == TipoNahual.MANTRA
            assert valor.valor == "entrada simulada"
        finally:
            builtins.input = original_input

    def test_errores_ejecucion(self, interpreter):
        """Prueba errores durante la ejecución."""
        with pytest.raises(ErrorNahual) as excinfo:
            interpreter.run('''
            espiritu x := 10;
            espiritu y := 0;
            espiritu resultado := x dividir y;
            ''')
        assert "División por cero" in str(excinfo.value)

    def test_conversion_tipos(self, interpreter):
        """Prueba la conversión entre tipos compatibles."""
        codigo = """
        energia decimal := 3.14;
        espiritu entero := convertir(decimal, "espiritu");
        mantra texto := convertir(entero, "mantra");
        """
        interpreter.run(codigo)
        assert interpreter.entorno_global.obtener_variable('entero').valor == 3
        assert interpreter.entorno_global.obtener_variable('texto').valor == "3"

    @pytest.mark.parametrize("programa_ejemplo", [
        "hola_mundo.nhl",
        "calculadora.nhl",
        "factorial.nhl",
        "fibonacci.nhl"
    ])
    def test_programas_ejemplo(self, interpreter, programa_ejemplo):
        """Prueba los programas de ejemplo incluidos."""
        ruta = Path("examples") / "programas" / programa_ejemplo
        with open(ruta, encoding='utf-8') as f:
            codigo = f.read()

        interpreter.run(codigo)
        # La prueba pasa si no hay excepciones

    def test_listas(self, interpreter):
        """Prueba el manejo de listas."""
        codigo = """
        lista numeros := [1, 2, 3];
        numeros.agregar(4);
        espiritu longitud := longitud(numeros);
        """
        interpreter.run(codigo)

        numeros = interpreter.entorno_global.obtener_variable('numeros')
        assert numeros.tipo == TipoNahual.LISTA
        assert len(numeros.valor.elementos) == 4
        assert interpreter.entorno_global.obtener_variable('longitud').valor == 4