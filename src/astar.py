"""
astar.py — A* Pathfinding Algorithm
DSA Project | Eduardo

Implementa A* estándar y bidireccional con heurística Euclidiana.
Se conecta con Maze (maze.py) y Visualizer (visualizer.py).

Refactor notes (branch fix/astar-cleanup):
  - astar()              : open_map reemplazado por g_score + came_from
                           (dos dicts separados, más limpio y sin Nodes stale)
  - astar_bidirectional(): closed_a/closed_b ahora son dict pos→Node;
                           condición de terminación correcta (no break prematuro);
                           reconstrucción del path arreglada;
                           _get_closed_node eliminada (era no-op)
"""

import heapq
import math
import time


# ─────────────────────────────────────────
#  Heurística
# ─────────────────────────────────────────


def heuristic(a, b):
    """
    Distancia Euclidiana — línea recta entre dos puntos en el grid.
    Sirve como estimación admisible del costo restante hasta el destino.
    """
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


# ─────────────────────────────────────────
#  Nodo interno del A*
# ─────────────────────────────────────────


class Node:
    """
    Representa una celda dentro del proceso de búsqueda A*.

    Atributos:
        pos     : (row, col) — posición en el grid
        g       : costo acumulado desde el inicio hasta este nodo
        h       : estimación heurística hasta el destino
        f       : g + h (prioridad en la open list)
        parent  : nodo desde el cual se llegó aquí (para reconstruir el path)
    """

    def __init__(self, pos, g=0, h=0, parent=None):
        self.pos = pos
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f


# ─────────────────────────────────────────
#  Algoritmo A* estándar
# ─────────────────────────────────────────


def astar(maze, start, end, callback=None):
    """
    Ejecuta A* desde `start` hasta `end` sobre un objeto Maze.

    Parámetros
    ----------
    maze        : instancia de Maze (maze.py)
    start       : (row, col) — celda de inicio
    end         : (row, col) — celda de destino
    callback    : función opcional llamada en cada paso con
                  (open_set_positions, closed_set_positions)
                  — usada por el visualizador para animar la búsqueda

    Retorna
    -------
    dict con:
        "path"          : lista de (row, col) desde start hasta end, o []
        "nodes_explored": cantidad de nodos sacados de la open list
        "time_ms"       : tiempo de ejecución en milisegundos
        "found"         : True si se encontró un camino
    """

    if maze.is_wall(*start):
        raise ValueError(f"El punto de inicio {start} es una pared.")
    if maze.is_wall(*end):
        raise ValueError(f"El punto de destino {end} es una pared.")
    if start == end:
        return {"path": [start], "nodes_explored": 0, "time_ms": 0.0, "found": True}

    # ── Estructuras de datos ───────────────────────────────────────────────
    #
    # open_heap : min-heap de (f, Node)
    #             Puede tener entradas duplicadas (lazy deletion).
    #             Una entrada es válida solo si coincide con g_score[pos].
    #
    # g_score   : pos → mejor g conocido hasta ahora.
    #             Es la fuente de verdad para saber si una entrada del heap
    #             es actual o stale.
    #
    # came_from : pos → Node padre.
    #             Reemplaza la cadena de punteros .parent en open_map.
    #             Se usa al final para reconstruir el camino.
    #
    # closed_set: set de posiciones ya procesadas definitivamente.
    #
    # open_set  : set de posiciones actualmente en el heap (para el callback).

    open_heap = []
    g_score = {start: 0}
    came_from = {}  # pos → Node padre (None para start)
    closed_set = set()
    open_set = {start}  # solo para el callback del visualizador

    start_node = Node(start, g=0, h=heuristic(start, end))
    heapq.heappush(open_heap, (start_node.f, start_node))

    nodes_explored = 0
    t_start = time.perf_counter()

    while open_heap:
        _, current = heapq.heappop(open_heap)

        # Entrada stale: ya existe un camino mejor a esta posición
        if current.g > g_score.get(current.pos, math.inf):
            continue

        # Entrada stale: ya fue procesada
        if current.pos in closed_set:
            continue

        closed_set.add(current.pos)
        open_set.discard(current.pos)
        nodes_explored += 1

        if callback:
            callback(open_set, closed_set)

        # ¡Destino alcanzado!
        if current.pos == end:
            elapsed = (time.perf_counter() - t_start) * 1000
            return {
                "path": _reconstruct_path(current.pos, came_from, start),
                "nodes_explored": nodes_explored,
                "time_ms": round(elapsed, 3),
                "found": True,
            }

        for neighbor_pos in maze.get_neighbors(*current.pos):
            if neighbor_pos in closed_set:
                continue

            g_new = g_score[current.pos] + 1  # costo uniforme

            # Solo procesamos si encontramos un camino mejor
            if g_new >= g_score.get(neighbor_pos, math.inf):
                continue

            # Actualizar tablas
            g_score[neighbor_pos] = g_new
            came_from[neighbor_pos] = current

            h_new = heuristic(neighbor_pos, end)
            neighbor_node = Node(neighbor_pos, g=g_new, h=h_new, parent=current)
            heapq.heappush(open_heap, (neighbor_node.f, neighbor_node))
            open_set.add(neighbor_pos)

    elapsed = (time.perf_counter() - t_start) * 1000
    return {
        "path": [],
        "nodes_explored": nodes_explored,
        "time_ms": round(elapsed, 3),
        "found": False,
    }


# ─────────────────────────────────────────
#  Bidirectional A* (extra ⭐)
# ─────────────────────────────────────────


def astar_bidirectional(maze, start, end, callback=None):
    """
    A* bidireccional — lanza dos búsquedas simultáneas: una desde `start`
    hacia `end` y otra desde `end` hacia `start`. Se detiene cuando la suma
    del mejor f de ambos frentes supera el mejor costo de encuentro encontrado,
    garantizando optimalidad.

    Misma firma de retorno que `astar()`.
    """

    if maze.is_wall(*start):
        raise ValueError(f"El punto de inicio {start} es una pared.")
    if maze.is_wall(*end):
        raise ValueError(f"El punto de destino {end} es una pared.")
    if start == end:
        return {"path": [start], "nodes_explored": 0, "time_ms": 0.0, "found": True}

    # ── Frente A: start → end ─────────────────────────────────────────────
    node_a = Node(start, g=0, h=heuristic(start, end))
    heap_a = [(node_a.f, node_a)]
    g_a = {start: 0}           # pos → mejor g conocido (frente A)
    closed_a = {}              # pos → Node (procesados frente A) ← DICT, no set

    # ── Frente B: end → start ─────────────────────────────────────────────
    node_b = Node(end, g=0, h=heuristic(end, start))
    heap_b = [(node_b.f, node_b)]
    g_b = {end: 0}             # pos → mejor g conocido (frente B)
    closed_b = {}              # pos → Node (procesados frente B) ← DICT, no set

    best_cost = math.inf
    meeting_pos = None

    nodes_explored = 0
    t_start = time.perf_counter()

    while heap_a and heap_b:

        # ── Condición de terminación óptima ───────────────────────────────
        # Si la suma de los mejores f de ambos frentes supera el mejor costo
        # encontrado, ninguna expansión futura puede mejorarlo → parar.
        top_f_a = heap_a[0][0]
        top_f_b = heap_b[0][0]
        if top_f_a + top_f_b >= best_cost:
            break

        # ── Expandir el frente con menor f en tope ────────────────────────
        # (equivalente a alternar pero más inteligente)
        expand_a = top_f_a <= top_f_b

        if expand_a:
            _, cur = heapq.heappop(heap_a)

            if cur.pos in closed_a:
                continue
            if cur.g > g_a.get(cur.pos, math.inf):
                continue

            closed_a[cur.pos] = cur
            nodes_explored += 1

            if callback:
                callback(
                    set(g_a) - set(closed_a),
                    set(closed_a),
                    set(g_b) - set(closed_b),
                    set(closed_b),
                )

            # ¿Este nodo ya fue procesado por el frente B?
            if cur.pos in closed_b:
                cost = closed_a[cur.pos].g + closed_b[cur.pos].g
                if cost < best_cost:
                    best_cost = cost
                    meeting_pos = cur.pos

            for nbr in maze.get_neighbors(*cur.pos):
                if nbr in closed_a:
                    continue
                g_new = g_a[cur.pos] + 1
                if g_new >= g_a.get(nbr, math.inf):
                    continue
                g_a[nbr] = g_new
                n = Node(nbr, g=g_new, h=heuristic(nbr, end), parent=cur)
                heapq.heappush(heap_a, (n.f, n))

        else:
            _, cur = heapq.heappop(heap_b)

            if cur.pos in closed_b:
                continue
            if cur.g > g_b.get(cur.pos, math.inf):
                continue

            closed_b[cur.pos] = cur
            nodes_explored += 1

            if callback:
                callback(
                    set(g_a) - set(closed_a),
                    set(closed_a),
                    set(g_b) - set(closed_b),
                    set(closed_b),
                )

            if cur.pos in closed_a:
                cost = closed_a[cur.pos].g + closed_b[cur.pos].g
                if cost < best_cost:
                    best_cost = cost
                    meeting_pos = cur.pos

            for nbr in maze.get_neighbors(*cur.pos):
                if nbr in closed_b:
                    continue
                g_new = g_b[cur.pos] + 1
                if g_new >= g_b.get(nbr, math.inf):
                    continue
                g_b[nbr] = g_new
                n = Node(nbr, g=g_new, h=heuristic(nbr, start), parent=cur)
                heapq.heappush(heap_b, (n.f, n))

    elapsed = (time.perf_counter() - t_start) * 1000

    if meeting_pos is not None:
        # Reconstruir ambas mitades desde el punto de encuentro
        path_a = _reconstruct_path_from_node(closed_a[meeting_pos])  # start → meeting
        path_b = _reconstruct_path_from_node(closed_b[meeting_pos])  # end   → meeting

        # path_b viene de end hacia meeting, hay que invertirlo
        # y eliminar el duplicado del meeting_pos (el [1:])
        full_path = path_a + path_b[1:][::-1]

        return {
            "path": full_path,
            "nodes_explored": nodes_explored,
            "time_ms": round(elapsed, 3),
            "found": True,
        }

    return {
        "path": [],
        "nodes_explored": nodes_explored,
        "time_ms": round(elapsed, 3),
        "found": False,
    }


# ─────────────────────────────────────────
#  Helpers privados
# ─────────────────────────────────────────


def _reconstruct_path(end_pos, came_from, start):
    """
    Reconstruye el camino desde came_from (usado por astar estándar).
    came_from: dict pos → Node padre.
    """
    path = [end_pos]
    current = came_from.get(end_pos)
    while current is not None:
        path.append(current.pos)
        current = came_from.get(current.pos)
    path.reverse()
    return path


def _reconstruct_path_from_node(node):
    """
    Recorre los punteros .parent desde el nodo final hasta la raíz.
    Usado por astar_bidirectional donde los Nodes viven en closed_a/closed_b.
    """
    path = []
    while node:
        path.append(node.pos)
        node = node.parent
    path.reverse()
    return path