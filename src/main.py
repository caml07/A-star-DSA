"""
main.py — Entry point del proyecto A* DSA
Conecta Maze, A* y Visualizer.
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog

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

# ─────────────────────────────────────────
#  UI Helpers (File Explorer & Menu)
# ─────────────────────────────────────────


def get_image_path():
    """Opens the native Windows/Mac File Explorer to pick a PNG/JPG."""
    root = tk.Tk()
    root.withdraw()  # Hide the ugly background Tkinter window
    root.attributes("-topmost", True)  # Force the file explorer to the front

    file_path = filedialog.askopenfilename(
        title="Select a Maze Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")],
    )

    root.destroy()
    return file_path


def show_start_menu():
    """Renders a Pygame start menu with clickable buttons."""
    pygame.init()

    screen = pygame.display.set_mode((500, 300))
    pygame.display.set_caption("A* Pathfinding - Main Menu")

    BG_COLOR = (18, 18, 18)
    BTN_COLOR = (70, 130, 220)
    TEXT_COLOR = (255, 255, 255)

    font = pygame.font.Font(None, 36)

    btn_default = pygame.Rect(100, 60, 300, 60)
    btn_upload = pygame.Rect(100, 160, 300, 60)

    while True:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, BTN_COLOR, btn_default, border_radius=8)
        pygame.draw.rect(screen, BTN_COLOR, btn_upload, border_radius=8)

        text_def = font.render("Load Default Maze", True, TEXT_COLOR)
        text_up = font.render("Upload Custom Image", True, TEXT_COLOR)

        screen.blit(
            text_def,
            (
                btn_default.centerx - text_def.get_width() // 2,
                btn_default.centery - text_def.get_height() // 2,
            ),
        )
        screen.blit(
            text_up,
            (
                btn_upload.centerx - text_up.get_width() // 2,
                btn_upload.centery - text_up.get_height() // 2,
            ),
        )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_default.collidepoint(event.pos):
                    return "default", None
                if btn_upload.collidepoint(event.pos):
                    path = get_image_path()
                    if path:
                        return "image", path


# ─────────────────────────────────────────
#  Main Application
# ─────────────────────────────────────────


def main():
    # 1. Show the cool Start Menu first!
    choice, img_path = show_start_menu()

    # 2. Load the requested maze
    maze = Maze()
    if choice == "default":
        maze.load_from_array(DEFAULT_MAZE)
    elif choice == "image":
        maze.load_from_image(img_path)

    # 3. Open the actual Visualizer Window
    viz = Visualizer(maze)
    algo = astar  # Defaulting to Eduardo's Bidirectional A*!

    # ── Loop principal de A* ───────────────────────────────────────────────
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
                if event.key == pygame.K_r:
                    viz._init_cell_colors()
                    viz.start = None
                    viz.end = None
                    state = "waiting_start"
                    viz.stats = {
                        "nodes_explored": 0,
                        "path_length": 0,
                        "time_ms": 0.0,
                        "status": "Click izquierdo para elegir inicio",
                    }

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = viz._pixel_to_cell(*pygame.mouse.get_pos())
                if not pos or maze.is_wall(*pos):
                    continue

                if event.button == 1 and state in ("waiting_start", "done"):
                    if state == "done":
                        viz.reset_search_colors()
                        viz.end = None
                        viz.stats["status"] = "Click izquierdo para elegir inicio"
                    viz.set_start(pos)
                    state = "waiting_end"
                    viz.stats["status"] = "Click derecho para elegir destino"

                elif event.button == 3 and state == "waiting_end":
                    viz.set_end(pos)
                    viz.stats["status"] = "Buscando..."
                    viz._draw_frame()

                    result = algo(maze, viz.start, viz.end, callback=viz.callback)

                    viz.stats.update(
                        {
                            "nodes_explored": result["nodes_explored"],
                            "path_length": len(result["path"]),
                            "time_ms": result["time_ms"],
                            "status": "Camino encontrado ✓  |  R para reiniciar"
                            if result["found"]
                            else "Sin camino ✗  |  R para reiniciar",
                        }
                    )
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
