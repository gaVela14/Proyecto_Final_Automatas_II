# TopScript — compilador (modelo base)

Lenguaje de dominio específico para presupuestos personales. Este código es el **modelo base** del compilador:
ya recorre todas las fases, de texto fuente a cuádruplos y ejecución de referencia. Algunas fases están
solo como esqueleto para que las complete cada integrante (ver `TAREAS.md`).

## Cómo correrlo
```
pip install -r requirements.txt          # instala PLY
python main.py tests/execution/presupuesto_basico.top
python main.py programa.top --tokens --ast --tabla --cuadruplos --opt
python main.py programa.top --asm salida.asm
python run_tests.py                      # corre toda la suite
```
| Opción | Qué muestra |
|---|---|
| `--tokens` | tokens del analizador léxico |
| `--ast` | árbol anotado con tipos (incluye las conversiones implícitas) |
| `--tabla` | tabla de símbolos y de direcciones |
| `--cuadruplos` | código intermedio (con `--opt`, ya optimizado) |
| `--opt` | aplica los pases del optimizador |
| `--asm FILE` | genera el esqueleto de ensamblador x86 |

## Fases y módulos
| Fase | Módulo | Estado |
|---|---|---|
| Léxico | `lexer.py` | listo |
| Sintáctico (GLC → árbol) | `parser.py`, `ast_nodes.py` | listo (falta `para cada`) |
| Semántico (Tema 1) | `semantico.py`, `tabla_simbolos.py`, `errores.py` | base lista |
| Código intermedio (Tema 2) | `codigo_intermedio.py` | expresiones, asignación, categorías, `si`, `mientras`; **faltan funciones** |
| Optimización (Tema 3) | `optimizador.py` | solo plegado de constantes (ejemplo) |
| Código objeto (Tema 4) | `codigo_objeto.py` | solo segmento de datos (esqueleto) |
| Referencia | `interprete.py` | listo: ejecuta los cuádruplos para verificar resultados |

## Resumen del lenguaje
```
presupuesto "Octubre" {
  decimal ingreso = 5000.0;
  constante decimal IVA = 0.16;
  categoria comida limite 1000.0 {        // abre un ámbito propio
    gasto 450.50 descripcion "super";     // suma a comida.gastado
  }
  si (comida.gastado > comida.limite) { alerta("Excedido"); } sino { mostrar("OK"); }
  funcion decimal doble(decimal x) { retornar x * 2; }
}
```
- Tipos: `entero`, `decimal`, `texto`, `logico`; `entero → decimal` se convierte solo (casting implícito).
- `+` con un `texto` concatena (convierte el otro operando). `/` siempre da `decimal`.
- Atributos de categoría: `.limite`, `.gastado`, `.nombre`.
- Palabras reservadas, incluidas `y`, `o`, `no`: no se pueden usar como nombres de variable.
- Extensión de los archivos fuente: `.top`.
