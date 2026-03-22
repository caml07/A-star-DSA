"""
astar.py — A* Pathfinding Algorithm
DSA Project | Eduardo

Implementa A* estándar y bidireccional con heurística Euclidiana.
Se conecta con Maze (maze.py) y Visualizer (visualizer.py).
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
        self.pos    = pos
        self.g      = g
        self.h      = h
        self.f      = g + h
        self.parent = parent

    # heapq compara por el primer elemento de la tupla;
    # al poner (f, node) necesitamos definir __lt__ para desempates.
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

    # Validaciones básicas
    if maze.is_wall(*start):
        raise ValueError(f"El punto de inicio {start} es una pared.")
    if maze.is_wall(*end):
        raise ValueError(f"El punto de destino {end} es una pared.")
    if start == end:
        return {"path": [start], "nodes_explored": 0, "time_ms": 0.0, "found": True}

    # Open list — min-heap ordenado por f
    # Cada entrada: (f, Node)
    open_heap = []
    start_node = Node(start, g=0, h=heuristic(start, end))
    heapq.heappush(open_heap, (start_node.f, start_node))

    # Diccionarios para acceso rápido
    open_map   = {start: start_node}   # pos → Node (en open list)
    closed_set = set()                  # posiciones ya procesadas

    nodes_explored = 0
    t_start = time.perf_counter()

    while open_heap:
        _, current = heapq.heappop(open_heap)

        # Si ya fue procesado (entrada duplicada en el heap), ignorar
        if current.pos in closed_set:
            continue

        closed_set.add(current.pos)
        open_map.pop(current.pos, None)
        nodes_explored += 1

        # Notificar al visualizador en cada paso
        if callback:
            callback(set(open_map.keys()), closed_set)

        # ¡Llegamos al destino!
        if current.pos == end:
            elapsed = (time.perf_counter() - t_start) * 1000
            return {
                "path":           _reconstruct_path(current),
                "nodes_explored": nodes_explored,
                "time_ms":        round(elapsed, 3),
                "found":          True,
            }

        # Expandir vecinos
        for neighbor_pos in maze.get_neighbors(*current.pos):
            if neighbor_pos in closed_set:
                continue

            g_new = current.g + 1  # costo uniforme (cada celda vale 1)
            h_new = heuristic(neighbor_pos, end)
            f_new = g_new + h_new

            # Si ya existe en open con menor o igual costo, no actualizar
            if neighbor_pos in open_map and open_map[neighbor_pos].g <= g_new:
                continue

            neighbor_node = Node(neighbor_pos, g=g_new, h=h_new, parent=current)
            heapq.heappush(open_heap, (f_new, neighbor_node))
            open_map[neighbor_pos] = neighbor_node

    # Se agotó la open list sin encontrar destino
    elapsed = (time.perf_counter() - t_start) * 1000
    return {
        "path":           [],
        "nodes_explored": nodes_explored,
        "time_ms":        round(elapsed, 3),
        "found":          False,
    }


# ─────────────────────────────────────────
#  Bidirectional A* (extra ⭐)
# ─────────────────────────────────────────

def astar_bidirectional(maze, start, end, callback=None):
    """
    A* bidireccional — lanza dos búsquedas simultáneas: una desde `start`
    hacia `end` y otra desde `end` hacia `start`. Se detiene cuando los dos
    frentes se encuentran, reduciendo el espacio explorado a ~la mitad.

    Misma firma de retorno que `astar()`.
    """

    if maze.is_wall(*start):
        raise ValueError(f"El punto de inicio {start} es una pared.")
    if maze.is_wall(*end):
        raise ValueError(f"El punto de destino {end} es una pared.")
    if start == end:
        return {"path": [start], "nodes_explored": 0, "time_ms": 0.0, "found": True}

    # Frente A: start → end
    node_a   = Node(start, g=0, h=heuristic(start, end))
    heap_a   = [(node_a.f, node_a)]
    map_a    = {start: node_a}
    closed_a = set()

    # Frente B: end → start
    node_b   = Node(end, g=0, h=heuristic(end, start))
    heap_b   = [(node_b.f, node_b)]
    map_b    = {end: node_b}
    closed_b = set()

    best_cost = math.inf
    meeting_a = None   # nodo del frente A en el punto de encuentro
    meeting_b = None   # nodo del frente B en el punto de encuentro

    nodes_explored = 0
    t_start = time.perf_counter()

    while heap_a and heap_b:

        # ── Expandir frente A ──────────────────
        _, cur_a = heapq.heappop(heap_a)
        if cur_a.pos not in closed_a:
            closed_a.add(cur_a.pos)
            map_a.pop(cur_a.pos, None)
            nodes_explored += 1

            if callback:
                callback(set(map_a.keys()), closed_a, set(map_b.keys()), closed_b)

            # ¿El frente A alcanzó algo que el frente B ya procesó?
            if cur_a.pos in closed_b:
                cost = cur_a.g + map_b.get(cur_a.pos, _get_closed_node(closed_b, cur_a.pos, node_b)).g
                if cost < best_cost:
                    best_cost = cost
                    meeting_a = cur_a
                    meeting_b = _find_node_in_closed(cur_a.pos, heap_b, closed_b, node_b)
                break

            for nbr in maze.get_neighbors(*cur_a.pos):
                if nbr in closed_a:
                    continue
                g_new = cur_a.g + 1
                if nbr not in map_a or map_a[nbr].g > g_new:
                    n = Node(nbr, g=g_new, h=heuristic(nbr, end), parent=cur_a)
                    heapq.heappush(heap_a, (n.f, n))
                    map_a[nbr] = n

        # ── Expandir frente B ──────────────────
        _, cur_b = heapq.heappop(heap_b)
        if cur_b.pos not in closed_b:
            closed_b.add(cur_b.pos)
            map_b.pop(cur_b.pos, None)
            nodes_explored += 1

            if callback:
                callback(set(map_a.keys()), closed_a, set(map_b.keys()), closed_b)

            if cur_b.pos in closed_a:
                cost = cur_b.g + map_a.get(cur_b.pos, node_a).g
                if cost < best_cost:
                    best_cost = cost
                    meeting_b = cur_b
                    meeting_a = _find_node_in_closed(cur_b.pos, heap_a, closed_a, node_a)
                break

            for nbr in maze.get_neighbors(*cur_b.pos):
                if nbr in closed_b:
                    continue
                g_new = cur_b.g + 1
                if nbr not in map_b or map_b[nbr].g > g_new:
                    n = Node(nbr, g=g_new, h=heuristic(nbr, start), parent=cur_b)
                    heapq.heappush(heap_b, (n.f, n))
                    map_b[nbr] = n

    elapsed = (time.perf_counter() - t_start) * 1000

    if meeting_a and meeting_b:
        path = _reconstruct_path(meeting_a) + _reconstruct_path(meeting_b)[1:][::-1]
        return {
            "path":           path,
            "nodes_explored": nodes_explored,
            "time_ms":        round(elapsed, 3),
            "found":          True,
        }

    return {
        "path":           [],
        "nodes_explored": nodes_explored,
        "time_ms":        round(elapsed, 3),
        "found":          False,
    }


# ─────────────────────────────────────────
#  Helpers privados
# ─────────────────────────────────────────

def _reconstruct_path(node):
    """Recorre los punteros `parent` desde el nodo final hasta el inicio."""
    path = []
    while node:
        path.append(node.pos)
        node = node.parent
    return path[::-1]


def _find_node_in_closed(pos, heap, closed, fallback):
    """Busca un nodo por posición en el heap (para el bidireccional)."""
    for _, node in heap:
        if node.pos == pos:
            return node
    return fallback


def _get_closed_node(closed_set, pos, fallback):
    """Placeholder — retorna fallback si pos no tiene nodo guardado."""
    return fallback