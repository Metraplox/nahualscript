# src/nahual/lexer.py
import ply.lex as lex
from .error_handler import LexError, LexPosition
from .logger import NahualLogger


class NahualLexer:
    """Analizador léxico para NahualScript."""

    tokens = [
        'ID',  # Identificadores
        'ESPIRITU_VAL',  # Valores numéricos enteros
        'ENERGIA_VAL',  # Valores numéricos decimales
        'MANTRA_VAL',  # Valores de texto
        'VERDAD_VAL',  # Valores booleanos
        'ASSIGN',  # :=
        'LPAREN',  # (
        'RPAREN',  # )
        'LBRACE',  # {
        'RBRACE',  # }
        'LBRACKET',  # [
        'RBRACKET',  # ]
        'COMMA',  # ,
        'SEMICOLON',  # ;
    ]

    reserved = {
        # Estructuras de control
        'ritual': 'RITUAL',  # while
        'vision': 'VISION',  # if
        'sino': 'SINO',  # else

        # Definición de funciones
        'sabiduria': 'SABIDURIA',  # function
        'retornar': 'RETORNAR',  # return

        # Tipos de datos
        'espiritu': 'ESPIRITU',  # int
        'energia': 'ENERGIA',  # float
        'mantra': 'MANTRA',  # string
        'verdad': 'VERDAD',  # bool
        'ofrenda': 'OFRENDA',  # list

        # Operadores
        'unir': 'UNIR',  # +
        'separar': 'SEPARAR',  # -
        'multiplicar': 'MULTIPLICAR',  # *
        'dividir': 'DIVIDIR',  # /
        'residuo': 'RESIDUO',  # %
        'y': 'Y',  # and
        'o': 'O',  # or
        'no': 'NO',  # not
        'igual': 'IGUAL',  # ==
        'mayor': 'MAYOR',  # >
        'menor': 'MENOR',  # <
        'mayor_igual': 'MAYOR_IGUAL',
        'menor_igual': 'MENOR_IGUAL',

        # Funciones del sistema
        'invocar': 'INVOCAR',  # print
        'percibir': 'PERCIBIR',  # input
        'convertir': 'CONVERTIR',
        'longitud': 'LONGITUD',

        # Valores de verdad
        'cierto': 'CIERTO',  # true
        'falso': 'FALSO',  # false
    }

    tokens = tokens + list(reserved.values())

    # Expresiones regulares simples
    t_ASSIGN = r':='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','
    t_SEMICOLON = r';'

    # Expresiones regulares con acciones
    def t_ENERGIA_VAL(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t

    def t_ESPIRITU_VAL(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_MANTRA_VAL(self, t):
        r'\"[^\"]*\"'
        t.value = t.value[1:-1]  # Eliminar comillas
        return t

    def t_VERDAD_VAL(self, t):
        r'cierto|falso'
        t.value = (t.value == 'cierto')
        return t

    @staticmethod
    def t_ID(t):
        r'[a-záéíóúñA-ZÁÉÍÓÚÑ_][a-záéíóúñA-ZÁÉÍÓÚÑ0-9_]*'
        t.type = NahualLexer.reserved.get(t.value, 'ID')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_COMMENT(self, t):
        r'//.*'
        pass

    def t_MULTILINE_COMMENT(self, t):
        r'/\*([^*]|\*[^/])*\*/'
        t.lexer.lineno += t.value.count('\n')
        pass

    t_ignore = ' \t'

    def t_error(self, t):
        pos = LexPosition(t.lineno, self.find_column(t))
        error = LexError(f"Carácter místico inválido '{t.value[0]}'", pos)
        self.error_collector.append(error)
        if self.debug:
            self.logger.error(str(error))
        t.lexer.skip(1)

    def find_column(self, token):
        """Encuentra la columna del token."""
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr

    def __init__(self, debug=False):
        self.debug = debug
        self.logger = NahualLogger(debug)
        self.error_collector = []
        self.lexer = lex.lex(module=self)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()

    def tokenize(self, data):
        self.input(data)
        tokens = []
        while True:
            tok = self.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens