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


def load_default_maze():
    maze_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "default_maze.txt"
    )
    matrix = []
    with open(maze_path, "r") as f:
        for line in f:
            row = [int(x) for x in line.strip().split(",")]
            matrix.append(row)
    return matrix


DEFAULT_MAZE = load_default_maze()

# ─────────────────────────────────────────
#  Paleta de colores compartida
# ─────────────────────────────────────────

C = {
    "bg":        (15,  15,  20),
    "panel":     (22,  22,  30),
    "border":    (45, 45, 60),
    "accent":    (80, 140, 255),
    "accent2":   (120, 80, 255),
    "text":      (230, 230, 240),
    "subtext":   (130, 130, 150),
    "btn":       (30,  30,  42),
    "btn_hov":   (45,  45,  65),
    "btn_sel":   (40,  70, 160),
    "green":     (60, 200, 120),
    "purple":    (150, 90, 255),
    "white":     (255, 255, 255),
}


def _load_image_surface(size):
    """Load the important.jpg image into a pygame Surface."""
    img_path = os.path.join(os.path.dirname(__file__), "..", "data", "importante.jpg")
    surf = pygame.image.load(img_path)
    return pygame.transform.smoothscale(surf, size)


def _draw_rounded_rect(surf, color, rect, radius=12, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def get_image_path():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Select a Maze Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")],
    )
    root.destroy()
    return path


# ─────────────────────────────────────────
#  Pantalla 1 — Selección de Maze
# ─────────────────────────────────────────

def show_maze_menu():
    """Pantalla 1: elegir entre maze default o imagen custom."""
    pygame.init()
    W, H = 560, 420
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("A* Pathfinding — DSA Project")
    clock = pygame.time.Clock()

    font_title  = pygame.font.SysFont("consolas", 22, bold=True)
    font_sub    = pygame.font.SysFont("consolas", 12)
    font_btn    = pygame.font.SysFont("consolas", 14, bold=True)
    font_label  = pygame.font.SysFont("consolas", 11)

    img = _load_image_surface((130, 130))

    # Botones
    btn_default = pygame.Rect(W//2 - 160, 280, 150, 52)
    btn_upload  = pygame.Rect(W//2 + 10,  280, 150, 52)

    tick = 0

    while True:
        clock.tick(60)
        tick += 1
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_default.collidepoint(event.pos):
                    return "default", None
                if btn_upload.collidepoint(event.pos):
                    path = get_image_path()
                    if path:
                        return "image", path

        screen.fill(C["bg"])

        # Sutil grid de puntos de fondo
        for gx in range(0, W, 28):
            for gy in range(0, H, 28):
                pygame.draw.circle(screen, C["border"], (gx, gy), 1)

        # Panel central
        panel = pygame.Rect(40, 24, W - 80, H - 48)
        _draw_rounded_rect(screen, C["panel"], panel, radius=16,
                           border=1, border_color=C["border"])

        # Imagen — lado izquierdo del panel
        img_x = panel.x + 24
        img_y = panel.y + 24
        img_rect = pygame.Rect(img_x, img_y, 130, 130)
        # Marco con borde accent
        _draw_rounded_rect(screen, C["border"],
                           img_rect.inflate(4, 4), radius=10)
        screen.blit(img, (img_x, img_y))

        # Badge encima de la imagen
        badge_text = font_label.render("imagen importante", True, C["accent"])
        bx = img_x + 130//2 - badge_text.get_width()//2
        pygame.draw.rect(screen, C["btn_sel"],
                         pygame.Rect(bx - 6, img_y - 20, badge_text.get_width() + 12, 18),
                         border_radius=4)
        screen.blit(badge_text, (bx, img_y - 18))

        # Texto lado derecho
        tx = img_x + 130 + 20
        ty = panel.y + 28

        # Título con acento de color
        t1 = font_title.render("A*", True, C["accent"])
        t2 = font_title.render(" Pathfinding", True, C["text"])
        screen.blit(t1, (tx, ty))
        screen.blit(t2, (tx + t1.get_width(), ty))

        sub1 = font_sub.render("DSA Project  ·  Eduardo / Steven / Luis", True, C["subtext"])
        screen.blit(sub1, (tx, ty + 30))

        # Línea separadora
        sep_y = ty + 52
        pygame.draw.line(screen, C["border"],
                         (tx, sep_y), (panel.right - 24, sep_y), 1)

        # Info tags
        tags = [("heurística", "Euclidiana"), ("grid", "2D"), ("viz", "Pygame")]
        tag_x = tx
        for label, val in tags:
            lw = font_label.render(f"{label}: ", True, C["subtext"])
            vw = font_label.render(val, True, C["accent"])
            screen.blit(lw, (tag_x, sep_y + 10))
            screen.blit(vw, (tag_x + lw.get_width(), sep_y + 10))
            tag_x += lw.get_width() + vw.get_width() + 14

        # Instrucción
        inst = font_sub.render("Paso 1 de 2  —  Elige el laberinto", True, C["subtext"])
        screen.blit(inst, (panel.x + panel.w//2 - inst.get_width()//2, 248))

        # Botones
        for btn, label, sublabel, col in [
            (btn_default, "Default Maze", "maze 10×10 .txt", C["accent"]),
            (btn_upload,  "Custom Image", "PNG / JPG / BMP", C["purple"]),
        ]:
            hov = btn.collidepoint(mx, my)
            bg  = C["btn_hov"] if hov else C["btn"]
            _draw_rounded_rect(screen, bg, btn, radius=10,
                               border=1, border_color=col)

            # Línea de acento superior
            accent_bar = pygame.Rect(btn.x + 10, btn.y, btn.w - 20, 2)
            pygame.draw.rect(screen, col, accent_bar, border_radius=1)

            lt = font_btn.render(label, True, C["text"])
            ls = font_label.render(sublabel, True, C["subtext"])
            screen.blit(lt, (btn.centerx - lt.get_width()//2, btn.y + 10))
            screen.blit(ls, (btn.centerx - ls.get_width()//2, btn.y + 30))

        # Footer
        footer = font_label.render("ESC para salir", True, C["border"])
        screen.blit(footer, (W//2 - footer.get_width()//2, H - 30))

        pygame.display.flip()

    return "default", None


# ─────────────────────────────────────────
#  Pantalla 2 — Selección de Algoritmo
# ─────────────────────────────────────────

def show_algo_menu():
    """Pantalla 2: elegir entre A* estándar y Bidireccional."""
    W, H = 560, 380
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("A* Pathfinding — DSA Project")
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("consolas", 22, bold=True)
    font_sub   = pygame.font.SysFont("consolas", 12)
    font_btn   = pygame.font.SysFont("consolas", 14, bold=True)
    font_label = pygame.font.SysFont("consolas", 11)

    btn_std  = pygame.Rect(W//2 - 200, 220, 175, 90)
    btn_bidir = pygame.Rect(W//2 + 25,  220, 175, 90)

    selected = None

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_std.collidepoint(event.pos):
                    return "standard"
                if btn_bidir.collidepoint(event.pos):
                    return "bidirectional"

        screen.fill(C["bg"])

        # Fondo punteado
        for gx in range(0, W, 28):
            for gy in range(0, H, 28):
                pygame.draw.circle(screen, C["border"], (gx, gy), 1)

        panel = pygame.Rect(40, 24, W - 80, H - 48)
        _draw_rounded_rect(screen, C["panel"], panel, radius=16,
                           border=1, border_color=C["border"])

        # Header
        t1 = font_title.render("A*", True, C["accent"])
        t2 = font_title.render(" Pathfinding", True, C["text"])
        cx = W//2 - (t1.get_width() + t2.get_width())//2
        screen.blit(t1, (cx, 44))
        screen.blit(t2, (cx + t1.get_width(), 44))

        inst = font_sub.render("Paso 2 de 2  —  Elige el algoritmo", True, C["subtext"])
        screen.blit(inst, (W//2 - inst.get_width()//2, 76))

        sep_y = 104
        pygame.draw.line(screen, C["border"], (panel.x + 20, sep_y),
                         (panel.right - 20, sep_y), 1)

        # Descripción
        desc = font_sub.render(
            "Ambos encuentran el camino óptimo — el bidireccional explora menos nodos.",
            True, C["subtext"])
        screen.blit(desc, (W//2 - desc.get_width()//2, 116))

        # Stats visuales
        stats = [
            ("velocidad",  "●●●●●", "●●●○○"),
            ("nodos",      "más",   "menos"),
        ]
        sx = W//2 - 120
        for i, (lbl, va, vb) in enumerate(stats):
            ly = 158 + i * 22
            lt = font_label.render(lbl, True, C["subtext"])
            la = font_label.render(va, True, C["accent"])
            lb = font_label.render(vb, True, C["purple"])
            screen.blit(lt, (sx - lt.get_width() - 8, ly))
            screen.blit(la, (sx + 10,  ly))
            screen.blit(lb, (sx + 130, ly))

        # Botones
        configs = [
            (btn_std,   "A* Estándar",       ["un frente de búsqueda", "clásico y confiable"], C["accent"]),
            (btn_bidir, "Bidireccional ⭐",   ["dos frentes simultáneos", "extra del proyecto"], C["purple"]),
        ]
        for btn, label, lines, col in configs:
            hov = btn.collidepoint(mx, my)
            bg  = C["btn_hov"] if hov else C["btn"]
            _draw_rounded_rect(screen, bg, btn, radius=10,
                               border=1, border_color=col)
            accent_bar = pygame.Rect(btn.x + 10, btn.y, btn.w - 20, 2)
            pygame.draw.rect(screen, col, accent_bar, border_radius=1)

            lt = font_btn.render(label, True, C["text"])
            screen.blit(lt, (btn.centerx - lt.get_width()//2, btn.y + 12))
            for i, line in enumerate(lines):
                ls = font_label.render(line, True, C["subtext"])
                screen.blit(ls, (btn.centerx - ls.get_width()//2, btn.y + 36 + i * 18))

        footer = font_label.render("ESC para salir", True, C["border"])
        screen.blit(footer, (W//2 - footer.get_width()//2, H - 30))

        pygame.display.flip()


# ─────────────────────────────────────────
#  Main Application
# ─────────────────────────────────────────

def main():
    # Pantalla 1 — maze
    choice, img_path = show_maze_menu()

    maze = Maze()
    if choice == "default":
        maze.load_from_array(DEFAULT_MAZE)
    elif choice == "image":
        maze.load_from_image(img_path)

    # Pantalla 2 — algoritmo
    algo_choice = show_algo_menu()
    algo = astar_bidirectional if algo_choice == "bidirectional" else astar

    viz = Visualizer(maze)

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

                    viz.stats.update({
                        "nodes_explored": result["nodes_explored"],
                        "path_length": len(result["path"]),
                        "time_ms": result["time_ms"],
                        "status": (
                            f"[{'Bidireccional' if algo_choice == 'bidirectional' else 'A* Estándar'}] "
                            + ("Camino encontrado ✓  |  R para reiniciar"
                               if result["found"]
                               else "Sin camino ✗  |  R para reiniciar")
                        ),
                    })
                    if result["found"]:
                        viz.mark_path(result["path"])

                    state = "done"

        viz._draw_frame()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()