"""
visualizer.py — Pygame Visualizer for A* Pathfinding
DSA Project | Luis
"""

import pygame
import sys

MAX_WINDOW_SIZE = 800
MARGIN = 1
STATS_HEIGHT = 100
FPS = 60

TITLE = "A* Pathfinding — DSA Project"

COLORS = {
    "empty": (255, 255, 255),
    "wall": (40, 40, 40),
    "start": (0, 200, 100),
    "end": (220, 50, 50),
    "open_list": (255, 220, 80),
    "closed_list": (255, 150, 50),
    "path": (70, 130, 220),
    "bidir": (160, 80, 220),
    "grid_line": (200, 200, 200),
    "background": (18, 18, 18),
    "stats_bg": (28, 28, 28),
    "stats_text": (220, 220, 220),
}


class Visualizer:
    def __init__(self, maze):
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.maze = maze
        self.rows = maze.rows
        self.cols = maze.cols

        safe_cols = max(1, self.cols)
        safe_rows = max(1, self.rows)

        cell_w = MAX_WINDOW_SIZE // safe_cols
        cell_h = MAX_WINDOW_SIZE // safe_rows
        self.cell_size = max(1, min(60, min(cell_w, cell_h)))

        self.grid_w = self.cols * self.cell_size
        self.grid_h = self.rows * self.cell_size
        self.win_w = max(self.grid_w, 400)
        self.win_h = self.grid_h + STATS_HEIGHT

        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        self.clock = pygame.time.Clock()

        self._rects = self._build_rects()
        self._bg = self._build_background()
        self._dirty: set = set()
        self._cell_color = {}
        self._init_cell_colors()

        self.stats = {
            "nodes_explored": 0,
            "path_length": 0,
            "time_ms": 0.0,
            "status": "Ready",
        }

        self.start = None
        self.end = None

    def _build_rects(self) -> dict:
        rects = {}
        current_margin = MARGIN if self.cell_size > 4 else 0
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * self.cell_size + current_margin
                y = r * self.cell_size + current_margin
                w = max(1, self.cell_size - current_margin * 2)
                h = max(1, self.cell_size - current_margin * 2)
                rects[(r, c)] = pygame.Rect(x, y, w, h)
        return rects

    def _build_background(self) -> pygame.Surface:
        bg = pygame.Surface((self.win_w, self.win_h))
        bg.fill(COLORS["background"])
        if self.cell_size > 4:
            for r in range(self.rows):
                for c in range(self.cols):
                    outer = pygame.Rect(
                        c * self.cell_size,
                        r * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    )
                    pygame.draw.rect(bg, COLORS["grid_line"], outer)
        return bg

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
        search_colors = {
            COLORS[k] for k in ("open_list", "closed_list", "path", "bidir")
        }
        for pos, color in list(self._cell_color.items()):
            if color in search_colors:
                self._set_cell(pos, "empty")

    def _draw_frame(self):
        self.screen.blit(self._bg, (0, 0))

        LAYER_ORDER = [
            "wall",
            "empty",
            "closed_list",
            "open_list",
            "bidir",
            "path",
            "start",
            "end",
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
                    center_x = rect.x + (rect.width // 2)
                    center_y = rect.y + (rect.height // 2)
                    pygame.draw.circle(self.screen, color, (center_x, center_y), 3)
                else:
                    pygame.draw.rect(self.screen, color, rect)

        self._dirty.clear()
        self._draw_stats()
        pygame.display.flip()

    def _draw_stats(self):
        panel = pygame.Rect(0, self.grid_h, self.win_w, STATS_HEIGHT)
        pygame.draw.rect(self.screen, COLORS["stats_bg"], panel)

        if not hasattr(self, "_font_cache"):
            self._font_cache = pygame.font.Font(None, 24)

        lines = [
            f"Status : {self.stats['status']}",
            f"Nodes  : {self.stats['nodes_explored']}   "
            f"Path   : {self.stats['path_length']} steps   "
            f"Time   : {self.stats['time_ms']} ms",
        ]
        for i, line in enumerate(lines):
            surf = self._font_cache.render(line, True, COLORS["stats_text"])
            self.screen.blit(surf, (14, self.grid_h + 15 + i * 28))

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self._init_cell_colors()
                    self.start = None
                    self.end = None
        return True

    def _pixel_to_cell(self, x, y):
        if y >= self.grid_h or x >= self.grid_w:
            return None
        r = y // self.cell_size
        c = x // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None

    def run(
        self,
        result: dict | None = None,
        animate: bool = False,
        animation_delay_ms: int = 30,
    ):
        if result:
            self.stats.update(
                {
                    "nodes_explored": result.get("nodes_explored", 0),
                    "path_length": len(result.get("path", [])),
                    "time_ms": result.get("time_ms", 0.0),
                    "status": "Path found" if result.get("found") else "No path",
                }
            )
            if result.get("found"):
                self.mark_path(result["path"])

        self._dirty = set(self._cell_color.keys())

        running = True
        while running:
            self.clock.tick(FPS)
            running = self._handle_events()

            if pygame.mouse.get_pressed()[0]:
                pos = self._pixel_to_cell(*pygame.mouse.get_pos())
                if pos and not self.maze.is_wall(*pos):
                    self.set_start(pos)
            elif pygame.mouse.get_pressed()[2]:
                pos = self._pixel_to_cell(*pygame.mouse.get_pos())
                if pos and not self.maze.is_wall(*pos):
                    self.set_end(pos)

            self._draw_frame()

        pygame.quit()
        sys.exit()

    def callback(
        self,
        open_positions: set,
        closed_positions: set,
        open_b: set | None = None,
        closed_b: set | None = None,
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
