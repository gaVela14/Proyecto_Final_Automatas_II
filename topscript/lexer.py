"""Analizador léxico de TopScript (PLY)."""
import ply.lex as lex
from errores import ERRORES

reservadas = {
    'presupuesto': 'PRESUPUESTO', 'categoria': 'CATEGORIA', 'limite': 'LIMITE',
    'gasto': 'GASTO', 'descripcion': 'DESCRIPCION', 'si': 'SI', 'sino': 'SINO',
    'mientras': 'MIENTRAS', 'alerta': 'ALERTA', 'mostrar': 'MOSTRAR',
    'entero': 'T_ENTERO', 'decimal': 'T_DECIMAL', 'texto': 'T_TEXTO',
    'logico': 'T_LOGICO', 'constante': 'CONSTANTE', 'funcion': 'FUNCION',
    'retornar': 'RETORNAR', 'verdadero': 'VERDADERO', 'falso': 'FALSO',
    'y': 'Y', 'o': 'O', 'no': 'NO',
}

tokens = [
    'ID', 'NUM_ENT', 'NUM_DEC', 'STRING',
    'MAS', 'MENOS', 'POR', 'DIV', 'LT', 'GT', 'LE', 'GE', 'EQ', 'NE', 'ASIGNA',
    'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'SEMI', 'DOT', 'COMMA',
] + list(reservadas.values())

t_MAS = r'\+'
t_MENOS = r'-'
t_POR = r'\*'
t_DIV = r'/'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_ASIGNA = r'='
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMI = r';'
t_DOT = r'\.'
t_COMMA = r','
t_ignore = ' \t\r'


def t_COMMENT(t):
    r'//[^\n]*'
    pass


def t_NUM_DEC(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_NUM_ENT(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'ID')
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    ERRORES.add('léxico', t.lexer.lineno, f"carácter no válido {t.value[0]!r}")
    t.lexer.skip(1)


def construir_lexer():
    lx = lex.lex()
    lx.lineno = 1
    return lx
