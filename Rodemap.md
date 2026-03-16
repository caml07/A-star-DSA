# 🗺️ Roadmap — Proyecto A\* DSA

> **Presentación:** Miércoles y/o Viernes  
> **Equipo:** Steven · Luis · Eduardo  
> **Stack:** Python + Pygame  
> **Objetivo:** Implementar A\* con visualizador GUI y competir contra otros equipos

---

## 👥 División de responsabilidades

| Integrante  | Capa                          | Archivos principales  |
| ----------- | ----------------------------- | --------------------- |
| **Eduardo** | Algoritmo (core A\*)          | `astar.py`, `main.py` |
| **Steven**  | Estructura del maze + Testing | `maze.py`, `tests/`   |
| **Luis**    | Visualización (Pygame)        | `visualizer.py`       |

---

## 📁 Estructura del proyecto

```
a-star-project/
├── src/
│   ├── maze.py          # Clase Maze, carga de grids
│   ├── astar.py         # Algoritmo A* (estándar + bidireccional)
│   ├── visualizer.py    # Render con Pygame
│   └── main.py          # Entry point
├── assets/
│   └── mazes/           # Archivos .txt/.json con mazes
├── tests/
│   └── test_astar.py    # Unit tests del algoritmo
├── requirements.txt
└── README.md
```

---

## 🚀 Fases

### Fase 1 — Setup & fundamentos `Días 1–2`

- [ ] **[Eduardo]** Crear repo privado en GitHub con estructura de carpetas base (`/src`, `/assets`, `/tests`, `/docs`)
- [ ] **[Eduardo]** Añadir a Steven y Luis como colaboradores — acordar branch strategy (`main` + feature branches)
- [ ] **[Todos]** Diseñar estructura del proyecto y documentar en README quién toca qué archivo
- [ ] **[Steven]** Implementar clase `Maze` — grid 2D, carga desde matriz o archivo, validación de paredes, soporte para cualquier tamaño
- [ ] **[Luis]** Setup de Pygame + ventana base — loop principal, render del grid, paleta de colores (vacío, pared, inicio, fin, path)

---

### Fase 2 — Core del A\* `Días 3–5`

- [ ] **[Eduardo]** Implementar A\* estándar — open/closed list, heurística Manhattan, reconstrucción del path, bien comentado
- [ ] **[Eduardo]** Heurísticas configurables — Manhattan (default), Euclidiana, Diagonal — como parámetro al ejecutar
- [ ] **[Luis]** Selector de inicio y fin con mouse — click izquierdo = inicio, click derecho = fin, validar que no caigan en paredes
- [ ] **[Luis]** Visualizar nodos explorados en tiempo real — colorear open list (amarillo) y closed list (naranja) mientras corre el algoritmo
- [ ] **[Steven]** Unit tests del algoritmo — mínimo 3 casos: path existe, no hay path, inicio == fin; verificar que el path es óptimo

---

### Fase 3 — Features de presentación `Días 6–8`

- [ ] **[Steven]** Cargar maze desde archivo `.txt` o `.json` con 1s y 0s — permite usar el maze fijo del profe sin hardcodear
- [ ] **[Luis]** Panel de estadísticas en pantalla — nodos explorados, longitud del path, tiempo de ejecución (ms)
- [ ] **[Luis + Eduardo]** Animación paso a paso con velocidad ajustable — slider o teclas para controlar la velocidad de visualización
- [ ] ⭐ **[Eduardo]** **(Extra)** Bidirectional A\* — dos frentes de búsqueda simultáneos desde inicio y fin, se encuentran en el medio

> **Nota:** El Bidirectional A\* es un extra para destacar frente al resto del salón. Si el tiempo aprieta, se puede omitir sin afectar el resto del proyecto.

---

### Fase 4 — Polish & presentación `Días 9–10`

- [ ] **[Luis]** UI/UX final — colores consistentes, fuente legible, leyenda de colores en pantalla, título del proyecto visible
- [ ] **[Steven]** README completo con instrucciones — cómo instalar (`pip install pygame`), cómo correr, cómo cargar un maze custom, capturas de pantalla
- [ ] **[Todos]** Preparar demo script para la presentación — qué teclas presionar, en qué orden mostrar features, practicar al menos una vez en grupo
- [ ] **[Todos]** Code review — pull requests de cada branch a `main`, verificar que el código esté comentado y limpio

---

## 🎨 Paleta de colores sugerida (Pygame)

| Estado               | Color       | RGB               |
| -------------------- | ----------- | ----------------- |
| Celda vacía          | Blanco      | `(255, 255, 255)` |
| Pared                | Gris oscuro | `(40, 40, 40)`    |
| Inicio               | Verde       | `(0, 200, 100)`   |
| Fin                  | Rojo        | `(220, 50, 50)`   |
| Open list            | Amarillo    | `(255, 220, 80)`  |
| Closed list          | Naranja     | `(255, 150, 50)`  |
| Path final           | Azul        | `(70, 130, 220)`  |
| Frente bidireccional | Púrpura     | `(160, 80, 220)`  |

---

## 📦 Instalación

```bash
git clone <repo-url>
cd a-star-project
pip install -r requirements.txt
python src/main.py
```

### `requirements.txt`

```
pygame>=2.5.0
```

---

## 🔀 Git workflow

```bash
# Crear tu rama de feature
git checkout -b feature/nombre-de-tu-feature

# Hacer commits descriptivos
git commit -m "feat: implementar heurística Manhattan"

# Push y abrir Pull Request a main
git push origin feature/nombre-de-tu-feature
```

> Convención de commits: `feat:` para features nuevas · `fix:` para bugs · `docs:` para documentación · `test:` para tests

---

## ✅ Criterios de éxito

- [x] El A\* encuentra el camino óptimo en cualquier maze válido
- [x] El usuario puede seleccionar inicio y fin con el mouse
- [x] La visualización muestra los nodos explorados en tiempo real
- [x] Se puede cargar el maze fijo del profesor desde archivo
- [x] El panel de estadísticas muestra nodos explorados, longitud y tiempo
- [ ] ⭐ Bidirectional A\* funcionando (extra)

---

_Última actualización: ver historial de commits_
