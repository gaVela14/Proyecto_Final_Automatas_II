"""Módulo de optimización (Tema 3).

Interfaz: cada PASE es una función  pase(quads) -> quads  (lista nueva, sin mutar la original).
Para agregar una técnica: escribir la función y añadirla a PASES.
El resultado optimizado debe producir EXACTAMENTE la misma salida que el original
(se verifica con el intérprete de referencia: run_tests.py).
"""
from codigo_intermedio import Quad, Const

NUM = ('entero', 'decimal')
ARIT = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, '*': lambda a, b: a * b}


def _es_num(a):
    return isinstance(a, Const) and a.tipo in NUM


def plegado_constantes(quads):
    """PASE DE EJEMPLO: evalúa en compilación operaciones con constantes y conversiones."""
    salida = []
    for q in quads:
        if q.op in ARIT and _es_num(q.arg1) and _es_num(q.arg2):
            tipo = 'entero' if q.arg1.tipo == q.arg2.tipo == 'entero' else 'decimal'
            v = ARIT[q.op](q.arg1.valor, q.arg2.valor)
            salida.append(Quad('=', Const(v, tipo), None, q.res))
        elif q.op == 'ENT_A_DEC' and _es_num(q.arg1):
            salida.append(Quad('=', Const(float(q.arg1.valor), 'decimal'), None, q.res))
        else:
            salida.append(q)
    return salida


# TODO Integrante 3: agregar aquí los demás pases (ver TAREAS.md)
PASES = [plegado_constantes]


def optimizar(quads):
    for pase in PASES:
        quads = pase(quads)
    return quads
