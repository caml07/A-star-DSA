"""
visualizer.py — Pygame Visualizer for A* Pathfinding
DSA Project | Luis

Refactor: panel de estadísticas movido al lado derecho del grid,
con estética oscura consistente con el menú de inicio.
"""

import pygame
import sys

MAX_GRID_SIZE = 740   # px máximos para el grid (ancho y alto)
MARGIN        = 1
STATS_W       = 220   # ancho del panel lateral de stats
FPS           = 60

TITLE = "A* Pathfinding — DSA Project"

# ── Paleta consistente con main.py ────────────────────────────────────────────
COLORS = {
    "empty":       (255, 255, 255),
    "wall":        (30,  30,  38),
    "start":       (60,  200, 120),
    "end":         (220, 60,  60),
    "open_list":   (255, 220, 80),
    "closed_list": (255, 150, 50),
    "path":        (80,  140, 255),
    "bidir":       (160, 80,  255),
    "grid_line":   (55,  55,  68),
    # UI
    "bg":          (15,  15,  20),
    "panel":       (22,  22,  30),
    "border":      (45,  45,  60),
    "accent":      (80,  140, 255),
    "accent2":     (120, 80,  255),
    "text":        (230, 230, 240),
    "subtext":     (130, 130, 150),
    "green":       (60,  200, 120),
    "red":         (220, 60,  60),
}

# Alias que el código existente usa
COLORS["background"] = COLORS["bg"]
COLORS["stats_bg"]   = COLORS["panel"]
COLORS["stats_text"] = COLORS["text"]


def _draw_rounded_rect(surf, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


class Visualizer:
    def __init__(self, maze):
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.maze = maze
        self.rows = maze.rows
        self.cols = maze.cols

        # Calcular tamaño de celda para que el grid quepa en MAX_GRID_SIZE
        cell_w = MAX_GRID_SIZE // max(1, self.cols)
        cell_h = MAX_GRID_SIZE // max(1, self.rows)
        self.cell_size = max(1, min(60, min(cell_w, cell_h)))

        self.grid_w = self.cols * self.cell_size
        self.grid_h = self.rows * self.cell_size

        # Ventana: grid a la izquierda, panel stats a la derecha
        self.win_w = self.grid_w + STATS_W
        self.win_h = max(self.grid_h, 480)   # mínimo para que el panel luzca bien

        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        self.clock  = pygame.time.Clock()

        self._rects      = self._build_rects()
        self._bg         = self._build_background()
        self._cell_color = {}
        self._dirty: set = set()
        self._init_cell_colors()

        # Fuentes
        self._font_mono_lg = pygame.font.SysFont("consolas", 13, bold=True)
        self._font_mono_sm = pygame.font.SysFont("consolas", 11)
        self._font_val     = pygame.font.SysFont("consolas", 22, bold=True)

        self.stats = {
            "nodes_explored": 0,
            "path_length":    0,
            "time_ms":        0.0,
            "status":         "Ready",
            "algo":           "A* Estándar",
        }

        self.start = None
        self.end   = None

    # ── Construcción del fondo ────────────────────────────────────────────────

    def _build_rects(self) -> dict:
        rects = {}
        m = MARGIN if self.cell_size > 4 else 0
        for r in range(self.rows):
            for c in range(self.cols):
                rects[(r, c)] = pygame.Rect(
                    c * self.cell_size + m,
                    r * self.cell_size + m,
                    max(1, self.cell_size - m * 2),
                    max(1, self.cell_size - m * 2),
                )
        return rects

    def _build_background(self) -> pygame.Surface:
        bg = pygame.Surface((self.win_w, self.win_h))
        bg.fill(COLORS["bg"])

        # Grid lines solo si las celdas son grandes
        if self.cell_size > 4:
            for r in range(self.rows):
                for c in range(self.cols):
                    outer = pygame.Rect(
                        c * self.cell_size, r * self.cell_size,
                        self.cell_size, self.cell_size,
                    )
                    pygame.draw.rect(bg, COLORS["grid_line"], outer)

        # Separador vertical entre grid y panel
        pygame.draw.line(
            bg, COLORS["border"],
            (self.grid_w, 0), (self.grid_w, self.win_h), 1,
        )
        return bg

    # ── Color de celdas ───────────────────────────────────────────────────────

    def _init_cell_colors(self):
        for r in range(self.rows):
            for c in range(self.cols):
                key = "wall" if self.maze.is_wall(r, c) else "empty"
                self._cell_color[(r, c)] = COLORS[key]
        self._dirty = set(self._cell_color.keys())

    def _set_cell(self, pos, color_key: str):
        if self.maze.is_wall(*pos):
            return
        new_color = COLORS[color_key]
        if self._cell_color.get(pos) != new_color:
            self._cell_color[pos] = new_color
            self._dirty.add(pos)

    def set_start(self, pos):
        if self.start:
            self._set_cell(self.start, "empty")
        self.start = pos
        self._set_cell(pos, "start")

    def set_end(self, pos):
        if self.end:
            self._set_cell(self.end, "empty")
        self.end = pos
        self._set_cell(pos, "end")

    def mark_open(self, positions):
        for pos in positions:
            if pos != self.start and pos != self.end:
                self._set_cell(pos, "open_list")

    def mark_closed(self, positions):
        for pos in positions:
            if pos != self.start and pos != self.end:
                self._set_cell(pos, "closed_list")

    def mark_path(self, path: list):
        for pos in path:
            if pos != self.start and pos != self.end:
                self._set_cell(pos, "path")

    def reset_search_colors(self):
        search = {COLORS[k] for k in ("open_list", "closed_list", "path", "bidir")}
        for pos, color in list(self._cell_color.items()):
            if color in search:
                self._set_cell(pos, "empty")

    # ── Render principal ──────────────────────────────────────────────────────

    def _draw_frame(self):
        self.screen.blit(self._bg, (0, 0))

        LAYER_ORDER = [
            "wall", "empty", "closed_list", "open_list",
            "bidir", "path", "start", "end",
        ]
        color_to_key = {COLORS[k]: k for k in LAYER_ORDER}
        layers = {k: [] for k in LAYER_ORDER}

        for pos, color in self._cell_color.items():
            key = color_to_key.get(color)
            if key:
                layers[key].append(pos)

        for key in LAYER_ORDER:
            color = COLORS[key]
            for pos in layers[key]:
                rect = self._rects[pos]
                if key == "path" and self.cell_size <= 4:
                    cx = rect.x + rect.width  // 2
                    cy = rect.y + rect.height // 2
                    pygame.draw.circle(self.screen, color, (cx, cy), 3)
                else:
                    pygame.draw.rect(self.screen, color, rect)

        self._dirty.clear()
        self._draw_stats_panel()
        pygame.display.flip()

    def _draw_stats_panel(self):
        """Panel lateral derecho con estadísticas al estilo del menú."""
        px = self.grid_w + 1      # x de inicio del panel (justo tras el separador)
        pw = STATS_W - 1
        ph = self.win_h

        # Fondo del panel
        pygame.draw.rect(self.screen, COLORS["panel"],
                         pygame.Rect(px, 0, pw, ph))

        # Puntos de fondo decorativos
        for gx in range(px + 14, px + pw, 22):
            for gy in range(14, ph, 22):
                pygame.draw.circle(self.screen, COLORS["border"], (gx, gy), 1)

        # ── Título / algo badge ───────────────────────────────────────────
        title_y = 18
        algo    = self.stats.get("algo", "A* Estándar")
        is_bidir = "idirec" in algo

        badge_color = COLORS["accent2"] if is_bidir else COLORS["accent"]
        badge_rect  = pygame.Rect(px + 12, title_y, pw - 24, 28)
        _draw_rounded_rect(self.screen, COLORS["bg"], badge_rect,
                           radius=6, border=1, border_color=badge_color)

        # Barra de acento superior del badge
        pygame.draw.rect(self.screen, badge_color,
                         pygame.Rect(px + 22, title_y, pw - 44, 2),
                         border_radius=1)

        label = self._font_mono_lg.render(algo, True, COLORS["text"])
        self.screen.blit(
            label,
            (px + pw // 2 - label.get_width() // 2, title_y + 7),
        )

        # ── Separador ─────────────────────────────────────────────────────
        sep_y = title_y + 42
        pygame.draw.line(self.screen, COLORS["border"],
                         (px + 12, sep_y), (px + pw - 12, sep_y), 1)

        # ── Tarjetas de métricas ──────────────────────────────────────────
        metrics = [
            ("NODOS",    str(self.stats["nodes_explored"]), COLORS["accent"]),
            ("PATH",     f"{self.stats['path_length']} pasos", COLORS["green"]),
            ("TIEMPO",   f"{self.stats['time_ms']} ms",   COLORS["accent2"]),
        ]

        card_y = sep_y + 14
        card_h = 62
        card_gap = 10

        for label_txt, val_txt, accent in metrics:
            card_rect = pygame.Rect(px + 12, card_y, pw - 24, card_h)
            _draw_rounded_rect(self.screen, COLORS["bg"], card_rect,
                               radius=8, border=1, border_color=COLORS["border"])

            # Línea de acento izquierda
            pygame.draw.rect(
                self.screen, accent,
                pygame.Rect(px + 12, card_y + 10, 3, card_h - 20),
                border_radius=2,
            )

            lbl = self._font_mono_sm.render(label_txt, True, COLORS["subtext"])
            val = self._font_val.render(val_txt, True, COLORS["text"])

            self.screen.blit(lbl, (px + 22, card_y + 8))
            self.screen.blit(val, (px + 22, card_y + 26))

            card_y += card_h + card_gap

        # ── Leyenda de colores ────────────────────────────────────────────
        legend_y = card_y + 8
        pygame.draw.line(self.screen, COLORS["border"],
                         (px + 12, legend_y), (px + pw - 12, legend_y), 1)
        legend_y += 12

        legend_lbl = self._font_mono_sm.render("LEYENDA", True, COLORS["subtext"])
        self.screen.blit(legend_lbl, (px + 12, legend_y))
        legend_y += 18

        legend_items = [
            ("Inicio",        "start"),
            ("Destino",       "end"),
            ("Open list",     "open_list"),
            ("Closed list",   "closed_list"),
            ("Path",          "path"),
            ("Bidir frente",  "bidir"),
        ]

        for name, key in legend_items:
            dot_rect = pygame.Rect(px + 14, legend_y + 2, 10, 10)
            pygame.draw.rect(self.screen, COLORS[key], dot_rect, border_radius=3)
            txt = self._font_mono_sm.render(name, True, COLORS["subtext"])
            self.screen.blit(txt, (px + 30, legend_y))
            legend_y += 18

        # ── Status ────────────────────────────────────────────────────────
        status_y = self.win_h - 70
        pygame.draw.line(self.screen, COLORS["border"],
                         (px + 12, status_y), (px + pw - 12, status_y), 1)
        status_y += 10

        status_txt = self.stats.get("status", "")
        # Colorear según resultado
        if "✓" in status_txt:
            s_color = COLORS["green"]
        elif "✗" in status_txt:
            s_color = COLORS["red"]
        else:
            s_color = COLORS["subtext"]

        # Partir en dos líneas si es largo
        words  = status_txt.split()
        lines  = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if self._font_mono_sm.size(test)[0] > pw - 28:
                lines.append(current)
                current = w
            else:
                current = test
        if current:
            lines.append(current)

        for line in lines[:3]:
            surf = self._font_mono_sm.render(line, True, s_color)
            self.screen.blit(surf, (px + 14, status_y))
            status_y += 16

        # Hint teclas
        hint_y = self.win_h - 20
        hint = self._font_mono_sm.render("R reiniciar  ·  ESC salir", True, COLORS["border"])
        self.screen.blit(hint, (px + pw // 2 - hint.get_width() // 2, hint_y))

    # ── Conversión pixel → celda ──────────────────────────────────────────────

    def _pixel_to_cell(self, x, y):
        # Ignorar clicks en el panel lateral
        if x >= self.grid_w or y >= self.grid_h:
            return None
        r = y // self.cell_size
        c = x // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None

    # ── Callback del algoritmo ────────────────────────────────────────────────

    def callback(
        self,
        open_positions:   set,
        closed_positions: set,
        open_b:   "set | None" = None,
        closed_b: "set | None" = None,
    ):
        self.mark_closed(closed_positions)
        self.mark_open(open_positions)

        if open_b is not None:
            for pos in open_b:
                if pos != self.start and pos != self.end:
                    self._set_cell(pos, "bidir")
        if closed_b is not None:
            self.mark_closed(closed_b)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.steps = getattr(self, "steps", 0) + 1

        if self.cell_size <= 4:
            if self.steps % 50 == 0:
                self._draw_frame()
        else:
            self._draw_frame()
            pygame.time.delay(30)