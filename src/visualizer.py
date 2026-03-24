"""
vizualizer.py — Pygame Visualizer for A* Pathfinding
DSA Project | Luis

Renders the maze grid and animates the A* search in real time.
Designed for efficiency:
  - Cell rects precomputed once at startup
  - Grid lines baked into a static background surface
  - Dirty-cell tracking so only changed cells are redrawn each frame
  - Clean separation between config, state, and drawing logic
"""

import pygame
import pygame._freetype
import sys

# ─────────────────────────────────────────
#  Config constants
# ─────────────────────────────────────────

CELL_SIZE = 60  # px per grid cell
MARGIN = 1  # px gap between cells (for grid lines)
STATS_HEIGHT = 80  # px reserved at the bottom for the stats panel
FPS = 60  # max frames per second

TITLE = "A* Pathfinding — DSA Project"

# ─────────────────────────────────────────
#  Color palette  (matches Roadmap spec)
# ─────────────────────────────────────────

COLORS = {
    "empty": (255, 255, 255),  # white      — open cell
    "wall": (40, 40, 40),  # dark gray  — blocked cell
    "start": (0, 200, 100),  # green      — start cell
    "end": (220, 50, 50),  # red        — end cell
    "open_list": (255, 220, 80),  # yellow     — frontier nodes
    "closed_list": (255, 150, 50),  # orange     — visited nodes
    "path": (70, 130, 220),  # blue       — final path
    "bidir": (160, 80, 220),  # purple     — bidirectional front
    "grid_line": (200, 200, 200),  # light gray — cell borders
    "background": (18, 18, 18),  # near-black — window background
    "stats_bg": (28, 28, 28),  # dark panel — stats area
    "stats_text": (220, 220, 220),  # off-white  — stats text
}


# ─────────────────────────────────────────
#  Visualizer class
# ─────────────────────────────────────────


class Visualizer:
    """
    Manages the Pygame window, grid rendering, and animation.

    Usage
    -----
    viz = Visualizer(maze)
    viz.run(result)                     # show a finished path
    viz.run(result, animate=True)       # animate the search step by step
    """

    def __init__(self, maze):
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.maze = maze
        self.rows = maze.rows
        self.cols = maze.cols

        # Window dimensions
        self.grid_w = self.cols * CELL_SIZE
        self.grid_h = self.rows * CELL_SIZE
        self.win_w = self.grid_w
        self.win_h = self.grid_h + STATS_HEIGHT

        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        self.clock = pygame.time.Clock()

        # Precompute one Rect per cell — avoids recalculating every frame
        self._rects = self._build_rects()

        # Static background surface with grid lines baked in
        self._bg = self._build_background()

        # Dirty tracking: set of (row, col) that need a redraw this frame
        self._dirty: set = set()

        # Current color state for every cell
        self._cell_color = {}
        self._init_cell_colors()

        # Stats to display in the panel
        self.stats = {
            "nodes_explored": 0,
            "path_length": 0,
            "time_ms": 0.0,
            "status": "Ready",
        }

        # Start + End positions (set by mouse or programmatically)
        self.start = None
        self.end = None

    # ── Setup helpers ──────────────────────────────────────────────────────

    def _build_rects(self) -> dict:
        """Precompute a pygame.Rect for each (row, col)."""
        rects = {}
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * CELL_SIZE + MARGIN
                y = r * CELL_SIZE + MARGIN
                w = CELL_SIZE - MARGIN * 2
                h = CELL_SIZE - MARGIN * 2
                rects[(r, c)] = pygame.Rect(x, y, w, h)
        return rects

    def _build_background(self) -> pygame.Surface:
        """
        Render grid lines once onto a Surface.
        Every frame we blit this surface first, then paint only dirty cells on top.
        """
        bg = pygame.Surface((self.win_w, self.win_h))
        bg.fill(COLORS["background"])

        # Draw grid-line gutters
        for r in range(self.rows):
            for c in range(self.cols):
                outer = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(bg, COLORS["grid_line"], outer)

        return bg

    def _init_cell_colors(self):
        """Set initial colors from the maze (wall vs empty)."""
        for r in range(self.rows):
            for c in range(self.cols):
                key = "wall" if self.maze.is_wall(r, c) else "empty"
                self._cell_color[(r, c)] = COLORS[key]
        self._dirty = set(self._cell_color.keys())  # full repaint on first frame

    # ── Color helpers ──────────────────────────────────────────────────────

    def _set_cell(self, pos, color_key: str):
        """Update a cell's color and mark it dirty (skip walls)."""
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
        """Wipe open/closed/path colors back to empty."""
        search_colors = {COLORS[k] for k in ("open_list", "closed_list", "path")}
        for pos, color in list(self._cell_color.items()):
            if color in search_colors:
                self._set_cell(pos, "empty")

    # ── Drawing ────────────────────────────────────────────────────────────

    def _draw_frame(self):
        """Blit background, repaint cells por capas, luego stats panel."""
        self.screen.blit(self._bg, (0, 0))

        # Orden de capas: el path y start/end siempre al último para no ser tapados
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

        # Agrupar celdas por capa
        layers = {k: [] for k in LAYER_ORDER}
        for pos, color in self._cell_color.items():
            key = color_to_key.get(color)
            if key:
                layers[key].append(pos)

        # Pintar capa por capa en el orden correcto
        for key in LAYER_ORDER:
            color = COLORS[key]
            for pos in layers[key]:
                pygame.draw.rect(self.screen, color, self._rects[pos])

        self._dirty.clear()
        self._draw_stats()
        pygame.display.flip()

    def _draw_stats(self):
        """Render the stats panel below the grid."""
        panel = pygame.Rect(0, self.grid_h, self.win_w, STATS_HEIGHT)
        pygame.draw.rect(self.screen, COLORS["stats_bg"], panel)

        if not hasattr(self, "_font_cache"):
            pygame._freetype.init()
            import os

            pygame_pkg = os.path.dirname(pygame.__file__)
            font_path = os.path.join(pygame_pkg, "freesansbold.ttf")
            self._font_cache = pygame._freetype.Font(font_path, 16)

        lines = [
            f"Status : {self.stats['status']}",
            f"Nodes  : {self.stats['nodes_explored']}   "
            f"Path   : {self.stats['path_length']} steps   "
            f"Time   : {self.stats['time_ms']} ms",
        ]
        for i, line in enumerate(lines):
            surf, _ = self._font_cache.render(line, COLORS["stats_text"])
            self.screen.blit(surf, (14, self.grid_h + 12 + i * 24))

    # ── Event handling ─────────────────────────────────────────────────────

    def _handle_events(self) -> bool:
        """
        Process Pygame events.
        Returns False if the user wants to quit, True otherwise.
        """
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
        """Convert a pixel coordinate to (row, col). Returns None if outside grid."""
        if y >= self.grid_h:
            return None
        r = y // CELL_SIZE
        c = x // CELL_SIZE
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None

    # ── Public API ─────────────────────────────────────────────────────────

    def run(
        self,
        result: dict | None = None,
        animate: bool = False,
        animation_delay_ms: int = 30,
    ):
        """
        Main loop.

        Parameters
        ----------
        result             : output from astar() — if provided, draws the path
        animate            : if True, replays the search step by step
                             (requires the result dict to contain 'steps')
        animation_delay_ms : ms between animation frames (lower = faster)
        """
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

        # Force full repaint on first frame
        self._dirty = set(self._cell_color.keys())

        running = True
        while running:
            self.clock.tick(FPS)
            running = self._handle_events()

            # Mouse: left click = start, right click = end
            if pygame.mouse.get_pressed()[0]:  # left
                pos = self._pixel_to_cell(*pygame.mouse.get_pos())
                if pos and not self.maze.is_wall(*pos):
                    self.set_start(pos)
            elif pygame.mouse.get_pressed()[2]:  # right
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
        """
        Hook for astar() / astar_bidirectional() to call on each step.
        Pass this method as the `callback` argument to either algorithm.

        Example
        -------
            result = astar(maze, start, end, callback=viz.callback)
        """
        self.mark_closed(closed_positions)
        self.mark_open(open_positions)

        if open_b is not None:
            for pos in open_b:
                if pos != self.start and pos != self.end:
                    self._set_cell(pos, "bidir")
        if closed_b is not None:
            self.mark_closed(closed_b)

        # Pump events so the window stays responsive during long searches
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self._draw_frame()
        pygame.time.delay(30)  # default animation speed — adjustable later


# ─────────────────────────────────────────
#  Standalone smoke-test
# ─────────────────────────────────────────

if __name__ == "__main__":
    """
    Quick sanity check — renders the default maze without running A*.
    Run with:  python src/vizualizer.py
    """
    import sys, os

    sys.path.insert(0, os.path.dirname(__file__))
    from maze import Maze

    SAMPLE = [
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

    m = Maze()
    m.load_from_array(SAMPLE)

    viz = Visualizer(m)
    viz.set_start((0, 0))
    viz.set_end((9, 9))
    viz.run()
