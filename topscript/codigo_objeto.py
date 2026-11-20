"""Generación de código objeto x86 / NASM (Tema 4).  ESQUELETO INICIAL.

Ya hace: segmento de datos (variables globales según la Tabla de Direcciones, temporales
y literales de texto) y un 'main' que lista cada cuádruplo como comentario.
Falta (Integrante 4): asignación de registros y traducción real de cada cuádruplo. Ver TAREAS.md.
"""
from codigo_intermedio import Const
from tabla_simbolos import TAM


def generar_asm(quads, tabla, tipos_temp):
    literales = {}
    for q in quads:
        for a in (q.arg1, q.arg2):
            if isinstance(a, Const) and a.tipo == 'texto' and a.valor not in literales:
                literales[a.valor] = f"str{len(literales)}"

    L = ["; TopScript -> x86 (NASM)   [ESQUELETO - pendiente: Tema 4]",
         "section .data"]
    for s in tabla.todos:
        if s.segmento == 'global':
            L.append(f"    {s.id_unico:<12} times {TAM[s.tipo]} db 0    ; {s.clase} {s.tipo}, offset {s.offset}")
    for t, tipo in tipos_temp.items():
        L.append(f"    {t:<12} times {TAM[tipo]} db 0    ; temporal {tipo}")
    for txt, nombre in literales.items():
        L.append(f'    {nombre:<12} db "{txt}", 0')
    L += ["", "section .text", "    global main", "", "main:"]
    for q in quads:
        L.append(f"    ; {q}")          # TODO Integrante 4: reemplazar por instrucciones x86
    L += ["    ; TODO: asignación de registros y traducción de cada cuádruplo",
          "    ret"]
    return "\n".join(L)
