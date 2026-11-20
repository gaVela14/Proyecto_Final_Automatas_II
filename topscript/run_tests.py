"""Ejecuta toda la suite:  python run_tests.py
 - tests/semantic     : cada archivo DEBE reportar al menos un error semántico
 - tests/intermediate : debe compilar; y la versión OPTIMIZADA debe dar la misma salida que la original
 - tests/execution    : debe compilar y ejecutarse sin errores (opt y sin opt dan la misma salida)
"""
import glob
import sys
from main import compilar
from errores import ERRORES
from interprete import Interprete


def correr(quads):
    return Interprete(quads).ejecutar()


def main():
    fallos = 0
    for ruta in sorted(glob.glob("tests/*/*.top")):
        carpeta = ruta.split("/")[1] if "/" in ruta else ruta.split("\\")[1]
        texto = open(ruta, encoding="utf-8").read()
        try:
            if carpeta == "semantic":
                compilar(texto)
                ok, detalle = ERRORES.hay(), f"{len(ERRORES.lista)} error(es) detectados"
            else:
                r = compilar(texto, usar_opt=False)
                if not r.ok:
                    ok, detalle = False, ERRORES.reporte()
                else:
                    base = correr(r.quads)
                    opt = compilar(texto, usar_opt=True).quads_opt
                    ok = base == correr(opt)
                    detalle = f"instrucciones {len(r.quads)} -> {len(opt)}" + ("" if ok else "  ¡LA SALIDA CAMBIÓ!")
        except NotImplementedError as e:
            ok, detalle = False, f"pendiente: {e}"
        fallos += 0 if ok else 1
        print(f"[{'OK ' if ok else 'FALLA'}] {ruta:<48} {detalle}")
    print(f"\n{'Todas las pruebas pasaron' if not fallos else str(fallos) + ' prueba(s) con fallas'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
