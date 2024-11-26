# src/nahual/parser.py

import ply.yacc as yacc
from typing import Any, List, Dict, Optional
from .lexer import NahualLexer
from .error_handler import ErrorSintaxis, Ubicacion

class NahualParser:
    """Parser para el lenguaje místico NahualScript."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.lexer = NahualLexer(debug)
        self.tokens = self.lexer.tokens
        self.ubicacion_actual = None
        self.parser = yacc.yacc(module=self)

    # Precedencia de operadores místicos
    precedence = (
        ('left', 'O'),
        ('left', 'Y'),
        ('left', 'IGUAL'),
        ('left', 'MENOR', 'MAYOR'),
        ('left', 'UNIR', 'SEPARAR'),
        ('left', 'MULTIPLICAR', 'DIVIDIR', 'RESIDUO'),
        ('right', 'NO'),
        ('right', 'UMENOS')
    )

    def p_programa(self, p):
        '''programa : declaraciones'''
        p[0] = ('programa', p[1], self._ubicacion(p))

    def p_declaraciones(self, p):
        '''declaraciones : declaracion
                         | declaraciones declaracion'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_declaracion(self, p):
        '''declaracion : var_declaracion
                      | funcion_declaracion
                      | ritual_declaracion
                      | vision_declaracion
                      | llamada_sistema
                      | retorno_stmt
                      | expresion SEMICOLON'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3 and p[2] == ';':
            p[0] = ('expresion_stmt', p[1], self._ubicacion(p))
        else:
            p[0] = p[1]

    def p_llamada_sistema(self, p):
        '''llamada_sistema : INVOCAR argumentos_invocar SEMICOLON
                         | PERCIBIR LPAREN expresion RPAREN SEMICOLON
                         | CONVERTIR LPAREN expresion COMMA expresion RPAREN SEMICOLON'''
        ubicacion = self._ubicacion(p)
        if p[1] == 'percibir':
            p[0] = ('llamada_sistema', 'percibir', [p[3]], ubicacion)
        elif p[1] == 'invocar':
            p[0] = ('llamada_sistema', 'invocar', p[2], ubicacion)
        elif p[1] == 'convertir':
            p[0] = ('llamada_sistema', 'convertir', [p[3], p[5]], ubicacion)

    def p_argumentos_invocar(self, p):
        '''argumentos_invocar : expresion
                            | argumentos_invocar UNIR expresion'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_var_declaracion(self, p):
        '''
        var_declaracion : tipo ID ASSIGN expresion SEMICOLON
                       | tipo ID ASSIGN llamada_sistema SEMICOLON
                       | tipo ID ASSIGN PERCIBIR LPAREN expresion RPAREN SEMICOLON
        '''
        tipo = p[1]
        nombre = p[2]
        ubicacion = self._ubicacion(p)

        if len(p) == 6:  # tipo ID := expresion;
            p[0] = ('var_declaracion', tipo, nombre, p[4], ubicacion)
        elif len(p) == 8:  # tipo ID := percibir(...);
            llamada = ('llamada_sistema', 'percibir', [p[6]], ubicacion)
            p[0] = ('var_declaracion', tipo, nombre, llamada, ubicacion)
        else:  # tipo ID := llamada_sistema;
            p[0] = ('var_declaracion', tipo, nombre, p[4], ubicacion)

    def p_tipo(self, p):
        '''tipo : ESPIRITU
               | ENERGIA
               | MANTRA
               | VERDAD
               | OFRENDA'''
        p[0] = p[1]

    def p_funcion_declaracion(self, p):
        '''funcion_declaracion : SABIDURIA ID LPAREN parametros_opt RPAREN bloque'''
        p[0] = ('funcion_declaracion', p[2], p[4], p[6], self._ubicacion(p))

    def p_ritual_declaracion(self, p):
        '''ritual_declaracion : RITUAL LPAREN expresion RPAREN bloque'''
        p[0] = ('ritual', p[3], p[5], self._ubicacion(p))

    def p_vision_declaracion(self, p):
        '''vision_declaracion : VISION LPAREN expresion RPAREN bloque sino_opt'''
        p[0] = ('vision', p[3], p[5], p[6], self._ubicacion(p))

    def p_sino_opt(self, p):
        '''sino_opt : SINO bloque
                   | empty'''
        p[0] = p[1] if len(p) > 2 else None

    def p_parametros_opt(self, p):
        '''parametros_opt : parametros
                        | empty'''
        p[0] = p[1] if p[1] is not None else []

    def p_parametros(self, p):
        '''parametros : parametro
                     | parametros COMMA parametro'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_parametro(self, p):
        '''parametro : tipo ID'''
        p[0] = (p[1], p[2])

    def p_bloque(self, p):
        '''bloque : LBRACE declaraciones RBRACE'''
        p[0] = ('bloque', p[2], self._ubicacion(p))

    def p_expresion(self, p):
        '''expresion : llamada_funcion
                    | llamada_sistema
                    | expresion UNIR expresion
                    | expresion SEPARAR expresion
                    | expresion MULTIPLICAR expresion
                    | expresion DIVIDIR expresion
                    | expresion RESIDUO expresion
                    | expresion IGUAL expresion
                    | expresion MENOR expresion
                    | expresion MAYOR expresion
                    | expresion Y expresion
                    | expresion O expresion
                    | NO expresion
                    | SEPARAR expresion %prec UMENOS
                    | LPAREN expresion RPAREN
                    | lista_literal
                    | acceso_lista
                    | ID
                    | ESPIRITU_VAL
                    | ENERGIA_VAL
                    | MANTRA_VAL
                    | VERDAD_VAL'''
        if len(p) == 2:
            if isinstance(p[1], str) and p.slice[1].type == 'ID':
                p[0] = ('variable', p[1], self._ubicacion(p))
            elif isinstance(p[1], tuple):
                p[0] = p[1]
            else:
                p[0] = ('literal', p[1], self._ubicacion(p))
        elif len(p) == 3:
            if p[1] == 'no':
                p[0] = ('operacion_unaria', 'no', p[2], self._ubicacion(p))
            else:
                p[0] = ('operacion_unaria', 'negativo', p[2], self._ubicacion(p))
        elif len(p) == 4:
            if p[1] == '(':
                p[0] = p[2]
            else:
                p[0] = ('operacion', p[2], p[1], p[3], self._ubicacion(p))
    def p_llamada_funcion(self, p):
        '''llamada_funcion : ID LPAREN argumentos_opt RPAREN'''
        p[0] = ('llamada_funcion', p[1], p[3], self._ubicacion(p))

    def p_argumentos_opt(self, p):
        '''argumentos_opt : argumentos
                        | empty'''
        p[0] = p[1] if p[1] is not None else []

    def p_argumentos(self, p):
        '''argumentos : expresion
                     | argumentos COMMA expresion'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_lista_literal(self, p):
        '''lista_literal : LBRACKET elementos_opt RBRACKET'''
        p[0] = ('lista', p[2], self._ubicacion(p))

    def p_elementos_opt(self, p):
        '''elementos_opt : elementos
                       | empty'''
        p[0] = p[1] if p[1] is not None else []

    def p_elementos(self, p):
        '''elementos : expresion
                    | elementos COMMA expresion'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_acceso_lista(self, p):
        '''acceso_lista : ID LBRACKET expresion RBRACKET'''
        p[0] = ('acceso_lista', ('variable', p[1], self._ubicacion(p)), p[3], self._ubicacion(p))

    def p_empty(self, p):
        '''empty :'''
        pass

    def p_retorno_stmt(self, p):
        """retorno_stmt : RETORNAR expresion SEMICOLON"""
        p[0] = ('retorno', p[2], self._ubicacion(p))

    def p_error(self, p):
        if p:
            ubicacion = Ubicacion(p.lineno, self.lexer.find_column(p))
            mensaje = f"Error en el ritual místico cerca de '{p.value}'"
            raise ErrorSintaxis(mensaje, ubicacion=ubicacion)
        else:
            raise ErrorSintaxis("El ritual está incompleto")

    def _ubicacion(self, p, indice: int = 1) -> Dict[str, Any]:
        """Obtiene la ubicación mística del token en el código fuente."""
        return {
            'linea': p.lineno(indice),
            'columna': getattr(p.slice[indice], 'lexpos', 0)
        }

    def parse(self, text: str) -> Optional[Any]:
        """Interpreta el ritual místico y retorna el árbol de sabidurías."""
        resultado = self.parser.parse(text, lexer=self.lexer, debug=self.debug)
        print("🌟 Árbol generado:", resultado)  # Agrega esta línea
        return resultado
