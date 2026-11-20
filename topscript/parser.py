"""Analizador sintáctico de TopScript (PLY / LALR(1)).
Cada producción construye un nodo del árbol (ast_nodes.py)."""
import ply.yacc as yacc
from lexer import tokens, construir_lexer
from errores import ERRORES
from ast_nodes import *

precedence = (
    ('left', 'O'),
    ('left', 'Y'),
    ('right', 'NO'),
    ('nonassoc', 'LT', 'GT', 'LE', 'GE', 'EQ', 'NE'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'POR', 'DIV'),
    ('right', 'UMENOS'),
)
start = 'programa'


def p_programa(p):
    'programa : PRESUPUESTO STRING LBRACE sentencias RBRACE'
    p[0] = Programa(p[2], p[4], linea=p.lineno(1))


def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | empty'''
    p[0] = [] if len(p) == 2 else p[1] + [p[2]]


def p_empty(p):
    'empty :'
    pass


def p_sentencia(p):
    '''sentencia : declaracion
                 | asignacion
                 | categoria
                 | gasto
                 | condicional
                 | ciclo
                 | accion
                 | funcion
                 | retorno
                 | llamada_sent'''
    p[0] = p[1]


def p_tipo(p):
    '''tipo : T_ENTERO
            | T_DECIMAL
            | T_TEXTO
            | T_LOGICO'''
    p[0] = p[1]


def p_declaracion(p):
    '''declaracion : tipo ID SEMI
                   | tipo ID ASIGNA expr SEMI
                   | CONSTANTE tipo ID ASIGNA expr SEMI'''
    if p[1] == 'constante':
        p[0] = Declaracion(p[2], p[3], p[5], True, linea=p.lineno(3))
    elif len(p) == 4:
        p[0] = Declaracion(p[1], p[2], None, False, linea=p.lineno(2))
    else:
        p[0] = Declaracion(p[1], p[2], p[4], False, linea=p.lineno(2))


def p_asignacion(p):
    'asignacion : ID ASIGNA expr SEMI'
    p[0] = Asignacion(p[1], p[3], linea=p.lineno(1))


def p_categoria(p):
    'categoria : CATEGORIA ID LIMITE expr bloque'
    p[0] = Categoria(p[2], p[4], p[5], linea=p.lineno(1))


def p_gasto(p):
    'gasto : GASTO expr DESCRIPCION expr SEMI'
    p[0] = Gasto(p[2], p[4], linea=p.lineno(1))


def p_condicional(p):
    '''condicional : SI LPAREN expr RPAREN bloque
                   | SI LPAREN expr RPAREN bloque SINO bloque'''
    p[0] = Si(p[3], p[5], p[7] if len(p) == 8 else None, linea=p.lineno(1))


def p_ciclo(p):
    'ciclo : MIENTRAS LPAREN expr RPAREN bloque'
    p[0] = Mientras(p[3], p[5], linea=p.lineno(1))


def p_bloque(p):
    'bloque : LBRACE sentencias RBRACE'
    p[0] = p[2]


def p_accion(p):
    '''accion : ALERTA LPAREN expr RPAREN SEMI
              | MOSTRAR LPAREN expr RPAREN SEMI'''
    p[0] = Accion(p[1], p[3], linea=p.lineno(1))


def p_funcion(p):
    'funcion : FUNCION tipo ID LPAREN params RPAREN bloque'
    p[0] = Funcion(p[2], p[3], p[5], p[7], linea=p.lineno(1))


def p_params(p):
    '''params : empty
              | lista_params'''
    p[0] = p[1] or []


def p_lista_params(p):
    '''lista_params : lista_params COMMA param
                    | param'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_param(p):
    'param : tipo ID'
    p[0] = (p[1], p[2])


def p_retorno(p):
    'retorno : RETORNAR expr SEMI'
    p[0] = Retornar(p[2], linea=p.lineno(1))


def p_llamada_sent(p):
    'llamada_sent : llamada SEMI'
    p[0] = LlamadaSent(p[1], linea=p[1].linea)


def p_llamada(p):
    'llamada : ID LPAREN args RPAREN'
    p[0] = Llamada(p[1], p[3], linea=p.lineno(1))


def p_args(p):
    '''args : empty
            | lista_args'''
    p[0] = p[1] or []


def p_lista_args(p):
    '''lista_args : lista_args COMMA expr
                  | expr'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


# ---------------- expresiones ----------------
def p_expr_bin(p):
    '''expr : expr MAS expr
            | expr MENOS expr
            | expr POR expr
            | expr DIV expr
            | expr LT expr
            | expr GT expr
            | expr LE expr
            | expr GE expr
            | expr EQ expr
            | expr NE expr
            | expr Y expr
            | expr O expr'''
    p[0] = Binario(p[2], p[1], p[3], linea=p.lineno(2))


def p_expr_neg(p):
    'expr : MENOS expr %prec UMENOS'
    p[0] = Unario('-', p[2], linea=p.lineno(1))


def p_expr_no(p):
    'expr : NO expr'
    p[0] = Unario('no', p[2], linea=p.lineno(1))


def p_expr_paren(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]


def p_expr_ent(p):
    'expr : NUM_ENT'
    p[0] = Literal(p[1], 'entero', linea=p.lineno(1))


def p_expr_dec(p):
    'expr : NUM_DEC'
    p[0] = Literal(p[1], 'decimal', linea=p.lineno(1))


def p_expr_str(p):
    'expr : STRING'
    p[0] = Literal(p[1], 'texto', linea=p.lineno(1))


def p_expr_verdadero(p):
    'expr : VERDADERO'
    p[0] = Literal(True, 'logico', linea=p.lineno(1))


def p_expr_falso(p):
    'expr : FALSO'
    p[0] = Literal(False, 'logico', linea=p.lineno(1))


def p_expr_id(p):
    'expr : ID'
    p[0] = Variable(p[1], linea=p.lineno(1))


def p_expr_acceso(p):
    'expr : ID DOT atributo'
    p[0] = Acceso(p[1], p[3], linea=p.lineno(1))


def p_atributo(p):
    '''atributo : ID
                | LIMITE'''
    p[0] = p[1]    # 'limite' es palabra reservada, pero también es atributo de categoría


def p_expr_llamada(p):
    'expr : llamada'
    p[0] = p[1]


def p_error(p):
    if any(e[0] == 'sintáctico' for e in ERRORES.lista):
        return  # solo se reporta el primer error sintáctico (evita cascadas)
    if p is None:
        ERRORES.add('sintáctico', 0, "fin de archivo inesperado (¿falta cerrar una llave?)")
    else:
        ERRORES.add('sintáctico', p.lineno, f"token inesperado {p.value!r}")


def construir_parser():
    return yacc.yacc(write_tables=False, debug=False)


def analizar_sintaxis(texto):
    """Devuelve el nodo Programa (o None si hubo errores)."""
    lexer = construir_lexer()
    parser = construir_parser()
    return parser.parse(texto, lexer=lexer, tracking=True)
