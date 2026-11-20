"""Tabla de símbolos (pila de ámbitos) y Tabla de direcciones de TopScript."""

TAM = {'entero': 4, 'decimal': 8, 'texto': 4, 'logico': 4, 'categoria': 20}
# categoria = limite(8) @0 + gastado(8) @8 + nombre(4) @16


class Simbolo:
    def __init__(self, nombre, clase, tipo, ambito, linea):
        self.nombre = nombre
        self.clase = clase          # variable | constante | parametro | categoria | funcion
        self.tipo = tipo            # tipo de dato (o tipo de retorno si es funcion)
        self.ambito = ambito        # nivel de anidamiento (0 = global)
        self.linea = linea
        self.inicializado = False
        self.segmento = None        # 'global' | 'local'   (tabla de direcciones)
        self.offset = None          # desplazamiento dentro del segmento
        self.id_unico = nombre      # nombre sin ambigüedad usado en los cuádruplos
        self.params = []            # solo funciones: [(tipo, nombre), ...]


class TablaSimbolos:
    def __init__(self):
        self.pila = [{}]            # una entrada (diccionario) por ámbito
        self.todos = []             # historial de todos los símbolos declarados
        self._usos = {}
        self._off = {'global': 0, 'local': 0}
        self.en_funcion = False

    @property
    def nivel(self):
        return len(self.pila) - 1

    def abrir_ambito(self):
        self.pila.append({})

    def cerrar_ambito(self):
        self.pila.pop()

    def iniciar_funcion(self):
        self.en_funcion = True
        self._off['local'] = 0

    def terminar_funcion(self):
        self.en_funcion = False

    def insertar(self, nombre, clase, tipo, linea):
        """Inserta en el ámbito actual. Devuelve None si ya existe ahí."""
        if nombre in self.pila[-1]:
            return None
        s = Simbolo(nombre, clase, tipo, self.nivel, linea)
        n = self._usos.get(nombre, 0)
        self._usos[nombre] = n + 1
        if n:
            s.id_unico = f"{nombre}_{n + 1}"
        if clase != 'funcion':
            seg = 'local' if self.en_funcion else 'global'
            s.segmento, s.offset = seg, self._off[seg]
            self._off[seg] += TAM[tipo]
        self.pila[-1][nombre] = s
        self.todos.append(s)
        return s

    def buscar(self, nombre):
        """Busca de el ámbito más interno al más externo."""
        for ambito in reversed(self.pila):
            if nombre in ambito:
                return ambito[nombre]
        return None

    def como_texto(self):
        filas = [f"{'Nombre':<12}{'Id único':<12}{'Clase':<11}{'Tipo':<10}"
                 f"{'Ámbito':<8}{'Segmento':<10}{'Offset':<8}{'Línea'}"]
        filas.append('-' * 78)
        for s in self.todos:
            filas.append(f"{s.nombre:<12}{s.id_unico:<12}{s.clase:<11}{s.tipo:<10}"
                         f"{s.ambito:<8}{(s.segmento or '-'):<10}"
                         f"{('-' if s.offset is None else s.offset):<8}{s.linea}")
        return "\n".join(filas)
