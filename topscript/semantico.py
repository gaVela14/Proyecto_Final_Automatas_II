"""Análisis semántico de TopScript (Tema 1).
Verifica tipos y ámbitos, inserta conversiones implícitas (casting) en el árbol
y llena la tabla de símbolos / direcciones."""
from ast_nodes import *
from tabla_simbolos import TablaSimbolos

NUM = ('entero', 'decimal')
ATRIBUTOS = {'limite': 'decimal', 'gastado': 'decimal', 'nombre': 'texto'}


def tiene_retorno(stmts):
    for s in stmts:
        if isinstance(s, Retornar):
            return True
        if isinstance(s, Si) and (tiene_retorno(s.entonces) or (s.sino and tiene_retorno(s.sino))):
            return True
        if isinstance(s, Mientras) and tiene_retorno(s.cuerpo):
            return True
    return False


class Semantico:
    def __init__(self, errores):
        self.err = errores
        self.tabla = TablaSimbolos()
        self.cats = []     # pila de categorías (símbolos) abiertas
        self.funcs = []    # pila de tipos de retorno de funciones abiertas

    # ---------- utilidades ----------
    def error(self, linea, msg):
        self.err.add('semántico', linea, msg)

    def analizar(self, prog):
        for s in prog.sentencias:
            self.stmt(s)
        return self.tabla

    def stmt(self, n):
        getattr(self, 'v_' + type(n).__name__)(n)

    def bloque(self, lista):
        self.tabla.abrir_ambito()
        for s in lista:
            self.stmt(s)
        self.tabla.cerrar_ambito()

    def expr(self, n):
        n.tipo = getattr(self, 'e_' + type(n).__name__)(n)
        return n.tipo

    def coercion(self, nodo, destino):
        """Envuelve 'nodo' en una Conversion si su tipo difiere del destino."""
        if nodo.tipo is None or nodo.tipo == destino:
            return nodo
        c = Conversion(destino, nodo, linea=nodo.linea)
        c.origen, c.tipo = nodo.tipo, destino
        return c

    def compat(self, destino, nodo, linea, ctx):
        """Compatibilidad de asignación: igual tipo, o entero -> decimal (implícito)."""
        t = nodo.tipo
        if t is None or t == destino:
            return nodo
        if destino == 'decimal' and t == 'entero':
            return self.coercion(nodo, 'decimal')
        self.error(linea, f"tipos incompatibles en {ctx}: no se puede asignar {t} a {destino}")
        return nodo

    def condicion(self, nodo, linea, que):
        t = self.expr(nodo)
        if t is not None and t != 'logico':
            self.error(linea, f"la condición de '{que}' debe ser lógica, no {t}")

    # ---------- expresiones ----------
    def e_Literal(self, n):
        return n.tipo

    def e_Variable(self, n):
        s = self.tabla.buscar(n.nombre)
        if s is None:
            self.error(n.linea, f"variable '{n.nombre}' no declarada en este ámbito")
            return None
        if s.clase in ('funcion', 'categoria'):
            self.error(n.linea, f"'{n.nombre}' es una {s.clase}, no una variable")
            return None
        n.simbolo = s
        return s.tipo

    def e_Acceso(self, n):
        s = self.tabla.buscar(n.obj)
        if s is None or s.clase != 'categoria':
            self.error(n.linea, f"'{n.obj}' no es una categoría declarada")
            return None
        if n.attr not in ATRIBUTOS:
            self.error(n.linea, f"la categoría '{n.obj}' no tiene el atributo '{n.attr}'")
            return None
        n.simbolo = s
        return ATRIBUTOS[n.attr]

    def e_Unario(self, n):
        t = self.expr(n.expr)
        if t is None:
            return None
        if n.op == '-' and t in NUM:
            return t
        if n.op == 'no' and t == 'logico':
            return 'logico'
        self.error(n.linea, f"operador '{n.op}' no válido para {t}")
        return None

    def e_Binario(self, n):
        ti, td = self.expr(n.izq), self.expr(n.der)
        if ti is None or td is None:
            return None
        op = n.op

        def mal():
            self.error(n.linea, f"operación '{op}' no válida entre {ti} y {td}")
            return None

        def a_decimal():
            n.izq, n.der = self.coercion(n.izq, 'decimal'), self.coercion(n.der, 'decimal')

        if op in ('+', '-', '*', '/'):
            if op == '+' and 'texto' in (ti, td):          # concatenación
                n.izq, n.der = self.coercion(n.izq, 'texto'), self.coercion(n.der, 'texto')
                return 'texto'
            if ti in NUM and td in NUM:
                if op == '/' or 'decimal' in (ti, td):
                    a_decimal()
                    return 'decimal'
                return 'entero'
            return mal()
        if op in ('<', '>', '<=', '>='):
            if ti in NUM and td in NUM:
                a_decimal() if ti != td else None
                return 'logico'
            return mal()
        if op in ('==', '!='):
            if ti == td:
                return 'logico'
            if ti in NUM and td in NUM:
                a_decimal()
                return 'logico'
            return mal()
        if op in ('y', 'o'):
            return 'logico' if ti == td == 'logico' else mal()
        return mal()

    def e_Llamada(self, n):
        tipos = [self.expr(a) for a in n.args]
        s = self.tabla.buscar(n.nombre)
        if s is None or s.clase != 'funcion':
            self.error(n.linea, f"función '{n.nombre}' no definida")
            return None
        if len(n.args) != len(s.params):
            self.error(n.linea, f"'{n.nombre}' espera {len(s.params)} argumento(s) y recibió {len(n.args)}")
        else:
            for i, (pt, pn) in enumerate(s.params):
                n.args[i] = self.compat(pt, n.args[i], n.linea, f"argumento '{pn}' de '{n.nombre}'")
        n.simbolo = s
        return s.tipo

    # ---------- sentencias ----------
    def v_Declaracion(self, n):
        if n.expr is not None:
            self.expr(n.expr)
            n.expr = self.compat(n.tipo_decl, n.expr, n.linea, f"la inicialización de '{n.nombre}'")
        s = self.tabla.insertar(n.nombre, 'constante' if n.es_const else 'variable', n.tipo_decl, n.linea)
        if s is None:
            self.error(n.linea, f"'{n.nombre}' ya fue declarado en este ámbito")
        else:
            s.inicializado = n.expr is not None
        n.simbolo = s

    def v_Asignacion(self, n):
        self.expr(n.expr)
        s = self.tabla.buscar(n.nombre)
        if s is None:
            self.error(n.linea, f"variable '{n.nombre}' no declarada en este ámbito")
            return
        if s.clase == 'constante':
            self.error(n.linea, f"no se puede modificar la constante '{n.nombre}'")
        elif s.clase in ('categoria', 'funcion'):
            self.error(n.linea, f"'{n.nombre}' es una {s.clase}; no admite asignación")
        else:
            n.expr = self.compat(s.tipo, n.expr, n.linea, f"la asignación a '{n.nombre}'")
            s.inicializado = True
        n.simbolo = s

    def v_Categoria(self, n):
        if self.funcs:
            self.error(n.linea, "las categorías solo pueden declararse a nivel de programa")
        t = self.expr(n.limite)
        if t is not None and t not in NUM:
            self.error(n.linea, f"el límite de '{n.nombre}' debe ser numérico, no {t}")
        else:
            n.limite = self.coercion(n.limite, 'decimal')
        s = self.tabla.insertar(n.nombre, 'categoria', 'categoria', n.linea)
        if s is None:
            self.error(n.linea, f"'{n.nombre}' ya fue declarado en este ámbito")
        else:
            s.inicializado = True
        n.simbolo = s
        self.cats.append(s)
        self.bloque(n.cuerpo)
        self.cats.pop()

    def v_Gasto(self, n):
        tm, td = self.expr(n.monto), self.expr(n.desc)
        if not self.cats:
            self.error(n.linea, "'gasto' solo puede usarse dentro de una categoría")
            return
        if tm is not None and tm not in NUM:
            self.error(n.linea, f"el monto de un gasto debe ser numérico, no {tm}")
        else:
            n.monto = self.coercion(n.monto, 'decimal')
        if td is not None and td != 'texto':
            self.error(n.linea, f"la descripción de un gasto debe ser texto, no {td}")
        n.simbolo = self.cats[-1]   # categoría a la que pertenece el gasto

    def v_Si(self, n):
        self.condicion(n.cond, n.linea, 'si')
        self.bloque(n.entonces)
        if n.sino:
            self.bloque(n.sino)

    def v_Mientras(self, n):
        self.condicion(n.cond, n.linea, 'mientras')
        self.bloque(n.cuerpo)

    def v_Accion(self, n):
        self.expr(n.expr)

    def v_LlamadaSent(self, n):
        self.expr(n.llamada)

    def v_Funcion(self, n):
        if self.funcs:
            self.error(n.linea, "no se permiten funciones anidadas")
        s = self.tabla.insertar(n.nombre, 'funcion', n.tipo_ret, n.linea)
        if s is None:
            self.error(n.linea, f"'{n.nombre}' ya fue declarado en este ámbito")
        else:
            s.params, s.inicializado = list(n.params), True
        n.simbolo = s
        self.tabla.abrir_ambito()
        self.tabla.iniciar_funcion()
        self.funcs.append(n.tipo_ret)
        n.param_simbolos = []
        for pt, pn in n.params:
            ps = self.tabla.insertar(pn, 'parametro', pt, n.linea)
            if ps is None:
                self.error(n.linea, f"parámetro '{pn}' repetido en '{n.nombre}'")
            else:
                ps.inicializado = True
                n.param_simbolos.append(ps)
        for st in n.cuerpo:
            self.stmt(st)
        if not tiene_retorno(n.cuerpo):
            self.error(n.linea, f"la función '{n.nombre}' no tiene ninguna instrucción 'retornar'")
        self.funcs.pop()
        self.tabla.terminar_funcion()
        self.tabla.cerrar_ambito()

    def v_Retornar(self, n):
        self.expr(n.expr)
        if not self.funcs:
            self.error(n.linea, "'retornar' solo puede usarse dentro de una función")
            return
        n.expr = self.compat(self.funcs[-1], n.expr, n.linea, "la instrucción 'retornar'")
