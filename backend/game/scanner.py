from __future__ import annotations

from backend.game.collision import EdgeKind, inspect_edge
from backend.models.cell import Side
from backend.models.maze import Maze
from backend.models.position import Position


def scan_horizontal(
    maze: Maze,
    start: Position,
    direction: Side,
    radius: int,
) -> tuple[int, bool]:
    if direction not in {Side.LEFT, Side.RIGHT}:
        raise ValueError("LMS работает только в направлениях left/right.")

    expected_sign = -1 if direction == Side.LEFT else 1
    current = start

    for distance in range(1, radius + 1):
        edge = inspect_edge(maze, current, direction)

        if edge.kind == EdgeKind.EXIT:#если LMS обнаружил выход то расстояние инвертируется
            return -expected_sign * distance, True

        if edge.kind == EdgeKind.WALL:
            if distance == 1:#наличие препятствия в соседней клетке можно узнать только движением
                return 0, False
            return expected_sign * distance, False

        if edge.target is None:
            if distance == 1:#наличие препятствия в соседней клетке можно узнать только движением
                return 0, False
            return expected_sign * distance, False

        current = edge.target#проход есть

    return 0, False#препятствия не обнаружены
