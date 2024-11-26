# tests/test_lexer.py
import pytest
from nahual.lexer import NahualLexer


def test_hola_mundo():
    lexer = NahualLexer()
    programa = '''
    // Mi primer programa en NahualScript
    sabiduria principal() {
        invocar "¡Hola, mundo místico!";
    }
    '''
    lexer.input(programa)
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)

    # Verificar tokens esperados
    assert len(tokens) == 8  # Contar tokens esperados
    assert tokens[0].type == 'FUNCTION'
    assert tokens[1].type == 'ID'