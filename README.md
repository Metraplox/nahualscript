# NahualScript

Un lenguaje de programación místico implementado en Python.


# Documentación Técnica

## Gramática del Lenguaje

### Tokens y Palabras Clave
```
TIPOS:
- espiritu (entero)
- energia (flotante)
- mantra (string)
- verdad (booleano)

CONTROL:
- vision (if)
- sino (else)
- ritual (while)

OPERADORES:
- unir (+)
- separar (-)
- multiplicar (*)
- dividir (/)
- residuo (%)
- y (&&)
- o (||)
- no (!)
```

### Estructura del Compilador

1. Análisis Léxico (lexer.py):
   - Tokenización usando PLY
   - Reconocimiento de palabras clave místicas
   - Manejo de errores léxicos con mensajes temáticos

2. Análisis Sintáctico (parser.py):
   - Gramática libre de contexto
   - Construcción de AST
   - Validación estructural

3. Sistema de Tipos (types.py):
   - Verificación estática
   - Inferencia de tipos
   - Conversiones implícitas

### Características Propias
1. Temática Mística:
   - Sintaxis inspirada en rituales y energías
   - Mensajes de error con emojis y terminología mística
   - Funciones con nombres ceremoniales

2. Sistema de Tipos Extendido:
   - Conversiones automáticas entre espiritu y energia
   - Validación de compatibilidad en operaciones
   - Manejo de errores contextual

3. Funciones Nativas:
   - invocarEspiritus() - Salida con formato místico
   - percibirEnergia() - Entrada con prompt místico
   - medirEnergia() - Medición de valores

## Instalación

1. Clonar el repositorio:
```bash
git clone [url-del-repo]
cd NahualScript
```


2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
```
3. Instalar dependencias:
```bash
pip install -r requirements.txt
pip install -e .
```


# Uso
```bash
`# Ejecutar un programa
nahual ejemplos/hola_mundo.nhl

# Modo debug
nahual --debug ejemplos/calculadora.nhl
```
# Desarrollo

Instalar dependencias de desarrollo:
```bash
pip install -r requirements.txt
```
Ejecutar pruebas:
```bash
pytest
```
Verificar estilo:
```bash
Copyblack .
pylint src tests
```