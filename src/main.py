"""
main.py — Entry point del proyecto A* DSA
Conecta Maze, A* y Visualizer.

Uso:
    python src/main.py
    python src/main.py --maze assets/mazes/example.txt
    python src/main.py --bidir
"""

import sys
import os
import argparse
import pygame

sys.path.insert(0, os.path.dirname(__file__))

from maze import Maze
from astar import astar, astar_bidirectional
from visualizer import Visualizer

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


def main():
    parser = argparse.ArgumentParser(description="A* Pathfinding — DSA Project")
    parser.add_argument("--maze",  type=str, default=None,
                        help="Ruta a un archivo .txt con el maze")
    parser.add_argument("--bidir", action="store_true",
                        help="Usa Bidirectional A* en lugar del estándar")
    args = parser.parse_args()

    # ── Cargar maze ────────────────────────────────────────────────────────
    maze = Maze()
    if args.maze:
        maze.load_from_file(args.maze)
    else:
        maze.load_from_array(DEFAULT_MAZE)

    # ── Abrir ventana ──────────────────────────────────────────────────────
    viz = Visualizer(maze)
    algo = astar_bidirectional if args.bidir else astar

    # ── Loop principal ─────────────────────────────────────────────────────
    # Estados: waiting_start → waiting_end → (corre A*) → done
    state = "waiting_start"
    viz.stats["status"] = "Click izquierdo para elegir inicio"

    running = True
    while running:
        viz.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # R = reiniciar sin cerrar la ventana
                if event.key == pygame.K_r:
                    viz._init_cell_colors()
                    viz.start = None
                    viz.end   = None
                    state = "waiting_start"
                    viz.stats = {"nodes_explored": 0, "path_length": 0,
                                 "time_ms": 0.0,
                                 "status": "Click izquierdo para elegir inicio"}

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = viz._pixel_to_cell(*pygame.mouse.get_pos())
                if not pos or maze.is_wall(*pos):
                    continue

                # Click izquierdo = elegir inicio
                if event.button == 1 and state in ("waiting_start", "done"):
                    if state == "done":
                        viz.reset_search_colors()
                        viz.end = None
                        viz.stats["status"] = "Click izquierdo para elegir inicio"
                    viz.set_start(pos)
                    state = "waiting_end"
                    viz.stats["status"] = "Click derecho para elegir destino"

                # Click derecho = elegir fin y correr el algoritmo
                elif event.button == 3 and state == "waiting_end":
                    viz.set_end(pos)
                    viz.stats["status"] = "Buscando..."
                    viz._draw_frame()

                    result = algo(maze, viz.start, viz.end, callback=viz.callback)

                    viz.stats.update({
                        "nodes_explored": result["nodes_explored"],
                        "path_length"   : len(result["path"]),
                        "time_ms"       : result["time_ms"],
                        "status"        : "Camino encontrado ✓  |  R para reiniciar"
                                          if result["found"] else
                                          "Sin camino ✗  |  R para reiniciar",
                    })
                    if result["found"]:
                        viz.mark_path(result["path"])
                        print("Found:", result["found"])
                        print("Path length:", len(result["path"]))

                    state = "done"

        viz._draw_frame()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()