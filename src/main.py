"""
main.py — Entry point del proyecto A* DSA
Conecta Maze, A* y Visualizer.

Uso:
    python src/main.py
    python src/main.py --maze assets/mazes/example.txt
    python src/main.py --bidir   (activa Bidirectional A*)
    python src/main.py --start 0,0 --end 9,9
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from maze import Maze
from astar import astar, astar_bidirectional

# ── Maze de ejemplo hardcodeado (mientras Luis termina el visualizador) ──
DEFAULT_MAZE = [
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
]

DEFAULT_START = (0, 0)
DEFAULT_END   = (9, 9)


def print_result(maze, result, start, end, bidir=False):
    """Imprime el resultado en consola con el path dibujado."""
    label = "Bidirectional A*" if bidir else "A*"
    print(f"\n{'─'*40}")
    print(f"  {label} — Resultado")
    print(f"{'─'*40}")

    if not result["found"]:
        print("  ✗ No se encontró un camino.")
    else:
        print(f"  ✓ Camino encontrado ({len(result['path'])} pasos)")

    print(f"  Nodos explorados : {result['nodes_explored']}")
    print(f"  Tiempo           : {result['time_ms']} ms")
    print(f"{'─'*40}\n")

    if result["found"]:
        path_set = set(result["path"])
        for r in range(maze.rows):
            row_str = ""
            for c in range(maze.cols):
                if (r, c) == start:
                    row_str += " S"
                elif (r, c) == end:
                    row_str += " E"
                elif (r, c) in path_set:
                    row_str += " ·"
                elif maze.grid[r][c] == 1:
                    row_str += " █"
                else:
                    row_str += "  "
            print(row_str)
        print()


def main():
    parser = argparse.ArgumentParser(description="A* Pathfinding — DSA Project")
    parser.add_argument("--maze",       type=str, default=None,
                        help="Ruta a un archivo de maze (.txt). Si no se da, usa el maze de ejemplo.")
    parser.add_argument("--bidir",      action="store_true",
                        help="Usa Bidirectional A* en lugar del estándar")
    parser.add_argument("--start",      type=str, default=None,
                        help="Inicio como 'row,col' (ej: 0,0)")
    parser.add_argument("--end",        type=str, default=None,
                        help="Destino como 'row,col' (ej: 9,9)")
    args = parser.parse_args()

    # Cargar maze
    maze = Maze()
    if args.maze:
        maze.load_from_file(args.maze)
    else:
        maze.load_from_array(DEFAULT_MAZE)
        print("  (Usando maze de ejemplo. Pasa --maze <archivo> para cargar uno propio)")

    # Parsear start/end
    start = DEFAULT_START
    end   = DEFAULT_END
    if args.start:
        r, c  = args.start.split(",")
        start = (int(r), int(c))
    if args.end:
        r, c = args.end.split(",")
        end  = (int(r), int(c))

    print(f"\n  Heurística : Euclidiana")
    print(f"  Inicio     : {start}")
    print(f"  Destino    : {end}")
    print(f"  Modo       : {'Bidirectional A*' if args.bidir else 'A* estándar'}")

    # Ejecutar
    algo = astar_bidirectional if args.bidir else astar
    result = algo(maze, start, end)

    print_result(maze, result, start, end, bidir=args.bidir)


if __name__ == "__main__":
    main()