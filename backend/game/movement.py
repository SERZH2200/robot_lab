from __future__ import annotations

from backend.models.cell import Side
from backend.models.maze import Maze
from backend.models.position import Position


def movement_result(maze: Maze, position: Position, side: Side) -> int:
    if side == Side.LEFT:
        return -1

    if side == Side.RIGHT:
        return 1

    target = maze.neighbor(position, Side.VERTICAL)
    if target is None:
        raise ValueError("Невозможно определить знак вертикального перемещения за границу лабиринта.")

    if target.row < position.row:
        return 1

    return -1
