"""Intérprete de referencia: ejecuta los cuádruplos directamente.
Sirve para comprobar que el compilador es correcto ANTES de generar ensamblador
(y después, para comparar su salida contra la del programa .asm)."""
from codigo_intermedio import Const


class ErrorEjecucion(Exception):
    pass


def _div(a, b):
    if b == 0:
        raise ErrorEjecucion("división entre cero")
    return a / b


BIN = {
    '+': lambda a, b: a + b, '-': lambda a, b: a - b, '*': lambda a, b: a * b, '/': _div,
    '<': lambda a, b: a < b, '>': lambda a, b: a > b, '<=': lambda a, b: a <= b,
    '>=': lambda a, b: a >= b, '==': lambda a, b: a == b, '!=': lambda a, b: a != b,
    'Y': lambda a, b: a and b, 'O': lambda a, b: a or b, 'CONCAT': lambda a, b: a + b,
}
UNA = {
    'NEG': lambda a: -a, 'NO': lambda a: not a,
    'ENT_A_DEC': float, 'ENT_A_TXT': str,
    'DEC_A_TXT': lambda a: f"{a:.2f}", 'LOG_A_TXT': lambda a: 'verdadero' if a else 'falso',
}


def formato(v, sufijo):
    if sufijo == 'DEC':
        return f"{v:.2f}"
    if sufijo == 'LOG':
        return 'verdadero' if v else 'falso'
    return str(v)


class Interprete:
    def __init__(self, quads, max_pasos=1_000_000):
        self.quads, self.max_pasos, self.mem = quads, max_pasos, {}

    def val(self, a):
        if isinstance(a, Const):
            return a.valor
        if a not in self.mem:
            raise ErrorEjecucion(f"'{a}' no tiene valor asignado")
        return self.mem[a]

    def ejecutar(self):
        etiquetas = {q.res: i for i, q in enumerate(self.quads) if q.op == 'LABEL'}
        salida, pc, pasos = [], 0, 0
        while pc < len(self.quads):
            q = self.quads[pc]
            pc += 1
            pasos += 1
            if pasos > self.max_pasos:
                raise ErrorEjecucion("se excedió el máximo de pasos (¿ciclo infinito?)")
            op = q.op
            if op == 'LABEL':
                continue
            if op == 'SALTA':
                pc = etiquetas[q.res]
            elif op == 'SI_FALSO':
                if not self.val(q.arg1):
                    pc = etiquetas[q.res]
            elif op == '=':
                self.mem[q.res] = self.val(q.arg1)
            elif op in BIN:
                self.mem[q.res] = BIN[op](self.val(q.arg1), self.val(q.arg2))
            elif op in UNA:
                self.mem[q.res] = UNA[op](self.val(q.arg1))
            elif op.startswith(('MOSTRAR_', 'ALERTA_')):
                clase, suf = op.split('_')
                txt = formato(self.val(q.arg1), suf)
                salida.append(("ALERTA: " if clase == 'ALERTA' else "") + txt)
            else:
                raise ErrorEjecucion(f"instrucción no soportada por el intérprete: {op}")
        return salida
