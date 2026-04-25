# A\* Pathfinding — DSA Project

> Implementación de A\* estándar y bidireccional con visualizador interactivo en Pygame.  
> Proyecto de Estructuras de Datos y Algoritmos · Keiser University

<br>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green?style=flat-square)
![License](https://img.shields.io/badge/License-GNU--3.0-orange?style=flat-square)

</div>

---

## Qué hace

- Resuelve laberintos con **A\* estándar** (un frente de búsqueda)
- Opcionalmente usa **A\* bidireccional** (dos frentes simultáneos, menos nodos explorados)
- **Visualiza en tiempo real** la open list, closed list y el path final
- Permite **cargar mazes custom** desde `.txt`, `.png` o `.jpg`
- Muestra estadísticas: nodos explorados, longitud del path y tiempo de ejecución

---

## Cómo correr

```bash
git clone https://github.com/caml07/A-star-DSA
cd A-star-DSA
pip install -r requirements.txt
python src/main.py
```

### Requisitos

```
pygame>=2.5.0
Pillow>=10.0.0
```

Python 3.10 o superior recomendado.

---

## Controles

| Acción                   | Control         |
| ------------------------ | --------------- |
| Colocar inicio           | Click izquierdo |
| Colocar destino          | Click derecho   |
| Reiniciar búsqueda       | `R`             |
| Volver al menú           | `M`             |
| Pausar / reanudar música | `P`             |
| Salir                    | `ESC`           |

Una vez colocado el destino, el algoritmo corre automáticamente.  
Después de ver el resultado, podés hacer click izquierdo para mover el inicio sin reiniciar el maze.

---

## Formatos de maze

**Archivo `.txt`** — una fila por línea, `0` = libre, `1` = pared.  
Soporta valores separados por comas o pegados (ambos formatos):

```
0,1,0,0,0
0,0,0,1,0
1,1,0,1,0
0,0,0,0,0
```

**Imagen `.png` / `.jpg`** — se convierte a un grid lógico de 41×41.  
Píxeles oscuros → pared. Píxeles claros → celda libre.

**Maze aleatorio** — generado con Recursive Backtracker (DFS), siempre tiene solución.

---

## Estructura del proyecto

```
A-star-DSA/
├── src/
│   ├── astar.py         # A* estándar + bidireccional (Eduardo)
│   ├── maze.py          # Clase Maze, loaders (Steven)
│   ├── visualizer.py    # Render con Pygame (Luis)
│   └── main.py          # Entry point y menús (Eduardo)
├── data/
│   ├── default_maze.txt # Maze de ejemplo 10×10
│   └── mymaze.txt       # Maze alternativo
├── tests/
│   ├── test_astar.py    # Unit tests del algoritmo (Steven)
│   └── test_maze.py     # Tests de Maze (Steven)
├── requirements.txt
└── README.md
```

---

## Algoritmos implementados

### A\* Estándar

Heurística Manhattan con tie-breaking sutil (`h × 1.0001`) para evitar explorar nodos laterales con el mismo costo. Usa `g_score` como dict separado en lugar de Nodes con estado mutable, lo que elimina entradas stale del heap sin necesitar lazy deletion explícito.

### A\* Bidireccional ⭐

Lanza dos búsquedas simultáneas desde el inicio y el destino. La condición de terminación es óptima: para cuando `f_top_A + f_top_B ≥ best_cost`, garantizando que no se pueda mejorar el camino encontrado. Típicamente explora significativamente menos nodos que el estándar en espacios abiertos.

---

## División de responsabilidades

| Integrante  | Rol                  | Archivos              |
| ----------- | -------------------- | --------------------- |
| **Eduardo** | Algoritmo core A\*   | `astar.py`, `main.py` |
| **Steven**  | Maze + Testing       | `maze.py`, `tests/`   |
| **Luis**    | Visualización Pygame | `visualizer.py`       |

---

## Tests

```bash
python tests/test_astar.py
```

Casos cubiertos: path existe, no hay path, inicio == fin, optimalidad del path, el path no atraviesa paredes.

---

## Paleta de colores

| Estado               | Color                      |
| -------------------- | -------------------------- |
| Celda libre          | Blanco                     |
| Pared                | Gris oscuro `(30, 30, 38)` |
| Inicio               | Verde `(60, 200, 120)`     |
| Destino              | Rojo `(220, 60, 60)`       |
| Open list            | Amarillo `(255, 220, 80)`  |
| Closed list          | Naranja `(255, 150, 50)`   |
| Path final           | Azul `(80, 140, 255)`      |
| Frente bidireccional | Púrpura `(160, 80, 255)`   |
