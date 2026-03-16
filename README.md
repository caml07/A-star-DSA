# A-star-DSA

El algoritmo este que nos dejo morales :D

---

## 👥 División de responsabilidades

| Integrante | Archivos Asignados | Descripción |
|------------|-------------------|-------------|
| **Eduardo** | `astar.py`, `main.py` | Algoritmo core A* (estándar + bidireccional) |
| **Steven** | `maze.py`, `tests/` | Estructura del maze + Testing |
| **Luis** | `visualizer.py` | Visualización con Pygame |

---

## 🗺️ Mini Roadmap — Progreso

### Fase 1 — Setup (Completado)
- ✅ **[Eduardo]** Crear repo y estructura base
- ✅ **[Eduardo]** Añadir colaboradores
- ✅ **[Todos]** Documentar responsabilidades

### Fase 2 — Core A* (Pendiente)
- [ ] Eduardo: Implementar A* estándar
- [ ] Eduardo: Heurísticas configurables
- [ ] Luis: Selector inicio/fin con mouse
- [ ] Luis: Visualizar nodos explorados
- [ ] Steven: Unit tests

### Fase 3 — Features (Pendiente)
- [ ] Steven: Cargar maze desde archivo
- [ ] Luis: Panel de estadísticas
- [ ] Luis + Eduardo: Animación paso a paso
- [ ] Eduardo: Bidirectional A* (extra)

### Fase 4 — Polish (Pendiente)
- [ ] Luis: UI/UX final
- [ ] Steven: README completo
- [ ] Todos: Demo y code review

---

## 📁 Estructura del proyecto

```
a-star-project/
├── src/
│   ├── maze.py          # Steven
│   ├── astar.py         # Eduardo
│   ├── visualizer.py    # Luis
│   └── main.py          # Eduardo
├── assets/mazes/
├── tests/test_astar.py  # Steven
├── requirements.txt
└── README.md
```

---

## 🚀 Cómo correr

```bash
pip install pygame
python src/main.py
```
