from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.models.cell import Side
from backend.models.maze import Maze
from backend.models.position import Position


class EdgeKind(str, Enum):
    OPEN = "open"
    WALL = "wall"
    EXIT = "exit"


@dataclass(frozen=True)
class EdgeInfo:
    kind: EdgeKind
    target: Position | None


def inspect_edge(maze: Maze, position: Position, side: Side) -> EdgeInfo:
    if maze.is_exit(position, side):
        return EdgeInfo(EdgeKind.EXIT, None)

    if maze.has_wall(position, side):
        return EdgeInfo(EdgeKind.WALL, None)

    return EdgeInfo(
        EdgeKind.OPEN,
        maze.neighbor(position, side),
    )
