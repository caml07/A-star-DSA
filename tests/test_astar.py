"""
test_astar.py — Unit Tests del algoritmo A*
DSA Project | Steven

Casos cubiertos:
  1. Path existe (maze simple con solución clara)
  2. No hay path (destino completamente bloqueado)
  3. Inicio == Fin
  4. El path retornado es óptimo (longitud mínima)
  5. El path no atraviesa paredes
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from maze import Maze
from astar import astar


# ─────────────────────────────────────────
#  Mazes de prueba
# ─────────────────────────────────────────

# Maze abierto — hay camino directo de (0,0) a (4,4)
OPEN_GRID = [
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0],
]

# Maze bloqueado — destino rodeado de paredes, sin solución
BLOCKED_GRID = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1],
    [0, 0, 1, 0, 1],
    [0, 0, 1, 1, 1],
]

# Maze lineal — camino único, longitud conocida
# De (0,0) a (0,4): exactamente 5 celdas, 4 pasos
LINEAR_GRID = [
    [0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
]


def make_maze(grid):
    m = Maze()
    m.load_from_array(grid)
    return m


# ─────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────

def assert_true(condition, msg):
    if not condition:
        raise AssertionError(f"FAIL — {msg}")

def assert_equal(a, b, msg):
    if a != b:
        raise AssertionError(f"FAIL — {msg} (esperado={b}, obtenido={a})")


# ─────────────────────────────────────────
#  Tests
# ─────────────────────────────────────────

def test_path_exists():
    """Caso 1: debe encontrar un camino cuando existe."""
    maze = make_maze(OPEN_GRID)
    result = astar(maze, (0, 0), (4, 4))

    assert_true(result["found"], "Se esperaba found=True en maze con solución")
    assert_true(len(result["path"]) > 0, "El path no debe estar vacío cuando found=True")
    assert_equal(result["path"][0], (0, 0), "El path debe comenzar en start")
    assert_equal(result["path"][-1], (4, 4), "El path debe terminar en end")

    print("  PASS — test_path_exists")


def test_no_path():
    """Caso 2: debe retornar found=False cuando el destino es inalcanzable."""
    maze = make_maze(BLOCKED_GRID)
    result = astar(maze, (0, 0), (3, 3))

    assert_true(not result["found"], "Se esperaba found=False en maze sin solución")
    assert_equal(result["path"], [], "El path debe ser [] cuando no hay solución")

    print("  PASS — test_no_path")


def test_start_equals_end():
    """Caso 3: start == end debe retornar un path de un solo nodo."""
    maze = make_maze(OPEN_GRID)
    result = astar(maze, (0, 0), (0, 0))

    assert_true(result["found"], "Se esperaba found=True cuando start==end")
    assert_equal(result["path"], [(0, 0)], "El path debe ser [start] cuando start==end")
    assert_equal(result["nodes_explored"], 0, "No se deben explorar nodos cuando start==end")

    print("  PASS — test_start_equals_end")


def test_path_is_optimal():
    """Caso 4: el path debe tener la longitud mínima posible."""
    maze = make_maze(LINEAR_GRID)
    result = astar(maze, (0, 0), (0, 4))

    assert_true(result["found"], "Se esperaba found=True en maze lineal")
    # De (0,0) a (0,4) en línea recta son 5 celdas (incluyendo start y end)
    assert_equal(len(result["path"]), 5, "El path óptimo en línea recta debe tener 5 celdas")

    print("  PASS — test_path_is_optimal")


def test_path_does_not_cross_walls():
    """Caso 5: ninguna celda del path debe ser una pared."""
    maze = make_maze(OPEN_GRID)
    result = astar(maze, (0, 0), (4, 4))

    assert_true(result["found"], "Se esperaba found=True para poder verificar el path")
    for pos in result["path"]:
        assert_true(
            not maze.is_wall(*pos),
            f"El path pasa por una pared en {pos}"
        )

    print("  PASS — test_path_does_not_cross_walls")


# ─────────────────────────────────────────
#  Runner
# ─────────────────────────────────────────

def run_all():
    tests = [
        test_path_exists,
        test_no_path,
        test_start_equals_end,
        test_path_is_optimal,
        test_path_does_not_cross_walls,
    ]

    print("\n==================================")
    print("  A* Unit Tests - DSA Project")
    print("==================================")

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR inesperado en {test.__name__}: {e}")
            failed += 1

    print("----------------------------------")
    print(f"  Resultado: {passed} passed / {failed} failed")
    print("==================================\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all()