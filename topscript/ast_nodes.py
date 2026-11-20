"""Nodos del árbol sintáctico / árbol de expresión de TopScript."""


class Nodo:
    campos = ()
    tipo = None      # tipo resultante (lo anota el análisis semántico)
    simbolo = None   # entrada de la tabla de símbolos (lo anota el semántico)

    def __init__(self, *args, linea=0):
        for c, v in zip(self.campos, args):
            setattr(self, c, v)
        self.linea = linea


# ---- sentencias ----
class Programa(Nodo):      campos = ('nombre', 'sentencias')
class Declaracion(Nodo):   campos = ('tipo_decl', 'nombre', 'expr', 'es_const')
class Asignacion(Nodo):    campos = ('nombre', 'expr')
class Categoria(Nodo):     campos = ('nombre', 'limite', 'cuerpo')
class Gasto(Nodo):         campos = ('monto', 'desc')
class Si(Nodo):            campos = ('cond', 'entonces', 'sino')
class Mientras(Nodo):      campos = ('cond', 'cuerpo')
class Accion(Nodo):        campos = ('clase', 'expr')          # alerta | mostrar
class Funcion(Nodo):       campos = ('tipo_ret', 'nombre', 'params', 'cuerpo')
class Retornar(Nodo):      campos = ('expr',)
class LlamadaSent(Nodo):   campos = ('llamada',)

# ---- expresiones ----
class Binario(Nodo):       campos = ('op', 'izq', 'der')
class Unario(Nodo):        campos = ('op', 'expr')
class Variable(Nodo):      campos = ('nombre',)
class Acceso(Nodo):        campos = ('obj', 'attr')            # categoria.atributo
class Llamada(Nodo):       campos = ('nombre', 'args')


class Conversion(Nodo):    # lo inserta el semántico (casting implícito)
    campos = ('destino', 'expr')
    origen = None


class Literal(Nodo):
    campos = ('valor',)

    def __init__(self, valor, tipo, linea=0):
        super().__init__(valor, linea=linea)
        self.tipo = tipo


def volcar(n, nivel=0, etiqueta=''):
    """Devuelve el árbol como lista de líneas de texto (para --ast)."""
    pad = '  ' * nivel
    if isinstance(n, Nodo):
        simples = [f"{c}={getattr(n, c, None)!r}" for c in n.campos
                   if not isinstance(getattr(n, c, None), (Nodo, list))]
        extra = f" : {n.tipo}" if n.tipo else ''
        out = [f"{pad}{etiqueta}{type(n).__name__}({', '.join(simples)}){extra}"]
        for c in n.campos:
            v = getattr(n, c, None)
            if isinstance(v, (Nodo, list)):
                out += volcar(v, nivel + 1, c + ': ')
        return out
    if isinstance(n, list):
        out = [f"{pad}{etiqueta}[{len(n)}]"]
        for x in n:
            out += volcar(x, nivel + 1)
        return out
    return [f"{pad}{etiqueta}{n!r}"]
