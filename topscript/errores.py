"""Gestor central de errores (léxicos, sintácticos y semánticos)."""


class GestorErrores:
    def __init__(self):
        self.lista = []  # (fase, linea, mensaje)

    def add(self, fase, linea, mensaje):
        if (fase, linea, mensaje) not in self.lista:   # evita duplicados idénticos
            self.lista.append((fase, linea, mensaje))

    def hay(self):
        return bool(self.lista)

    def limpiar(self):
        self.lista = []

    def reporte(self):
        return "\n".join(f"[{f}] línea {l}: {m}" for f, l, m in self.lista)


ERRORES = GestorErrores()
