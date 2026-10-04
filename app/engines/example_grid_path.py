"""EXAMPLE ENGINE 2: shortest path on a grid field (A*).

Pattern for navigation, routing and field-based problems. Grid legend:
S start, G goal, # wall, . free.
"""
import heapq

from .base import Engine, EngineError, make_result


def _parse(data):
    rows = data.get("grid")
    if not isinstance(rows, list) or not rows or not all(isinstance(r, str) for r in rows):
        raise EngineError("grid must be a list of strings")
    width = len(rows[0])
    if width == 0 or any(len(r) != width for r in rows):
        raise EngineError("all grid rows must have the same non-zero length")
    if len(rows) > 100 or width > 100:
        raise EngineError("grid at most 100x100")
    start = goal = None
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch not in "S.G#":
                raise EngineError(f"unknown cell {ch!r} at row {r}, col {c}")
            if ch == "S":
                if start:
                    raise EngineError("more than one S")
                start = (r, c)
            elif ch == "G":
                if goal:
                    raise EngineError("more than one G")
                goal = (r, c)
    if not start or not goal:
        raise EngineError("grid needs exactly one S and one G")
    return rows, start, goal


def _astar(rows, start, goal):
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    open_heap = [(h(start), 0, start)]
    came, best_g, explored = {}, {start: 0}, 0
    while open_heap:
        _, g, cur = heapq.heappop(open_heap)
        if g > best_g.get(cur, 1 << 30):
            continue
        explored += 1
        if cur == goal:
            path = [cur]
            while cur in came:
                cur = came[cur]
                path.append(cur)
            return path[::-1], explored
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = cur[0] + dr, cur[1] + dc
            if 0 <= nr < len(rows) and 0 <= nc < len(rows[0]) and rows[nr][nc] != "#":
                ng = g + 1
                if ng < best_g.get((nr, nc), 1 << 30):
                    best_g[(nr, nc)] = ng
                    came[(nr, nc)] = cur
                    heapq.heappush(open_heap, (ng + h((nr, nc)), ng, (nr, nc)))
    return None, explored


class GridPath(Engine):
    name = "grid_path"
    description = "Shortest path on a grid field using A*."

    def sample_input(self):
        return {
            "grid": [
                "S...#.....",
                ".##.#.###.",
                ".#..#...#.",
                ".#.####.#.",
                ".#......#.",
                ".######.#.",
                "........#G",
            ]
        }

    def run(self, data):
        rows, start, goal = _parse(data)
        path, explored = _astar(rows, start, goal)
        if path is None:
            return make_result(
                self.name,
                summary={"path_found": "no", "cells_explored": explored},
                grid={"rows": rows, "path": []},
                log=["No route exists between S and G."],
            )
        return make_result(
            self.name,
            summary={"path_found": "yes", "steps": len(path) - 1, "cells_explored": explored},
            table=[{"step": i, "row": p[0], "col": p[1]} for i, p in enumerate(path)],
            grid={"rows": rows, "path": [list(p) for p in path]},
            log=["A* expands the cell with the lowest steps-so-far plus Manhattan distance to the goal."],
        )
