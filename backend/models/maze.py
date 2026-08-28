from __future__ import annotations

from dataclasses import dataclass, field

from backend.models.cell import Side, TriangleOrientation
from backend.models.position import Position


@dataclass(frozen=True, slots=True)
class ExitEdge:
    position: Position
    side: Side


@dataclass
class Maze:#модель лабиринта
    rows: int
    cols: int
    start: Position
    exit_edge: ExitEdge
    lms_radius: int = 5
    lms_start_direction: Side = Side.LEFT
    walls: dict[Position, set[Side]] = field(default_factory=dict)

    def __post_init__(self) -> None:#dataclass автоматически вызывает после конструктора
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("Размеры лабиринта должны быть положительными.")

        if self.lms_radius <= 0:
            raise ValueError("Радиус LMS должен быть положительным.")

        if not self.contains(self.start):
            raise ValueError("Начальная позиция робота находится вне лабиринта.")

        if not self.contains(self.exit_edge.position):
            raise ValueError("Клетка выхода находится вне лабиринта.")

        if self.exit_edge.side == Side.VERTICAL:
            if self.neighbor(self.exit_edge.position, Side.VERTICAL) is not None:
                raise ValueError("Вертикальный выход должен находиться на внешней границе лабиринта.")
        elif self.neighbor(self.exit_edge.position, self.exit_edge.side) is not None:
            raise ValueError("Выход должен находиться на внешней границе лабиринта.")

    def contains(self, position: Position) -> bool:#принадлжеит ли позиция лабиринту
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols
#ориентация клетки в зависимости от положения
    def orientation(self, position: Position) -> TriangleOrientation:
        if (position.row + position.col) % 2 == 0:
            return TriangleOrientation.UP
        return TriangleOrientation.DOWN

    def neighbor(self, position: Position, side: Side) -> Position | None:
        if side == Side.LEFT:
            candidate = Position(position.row, position.col - 1)
        elif side == Side.RIGHT:
            candidate = Position(position.row, position.col + 1)
        else:
            if self.orientation(position) == TriangleOrientation.UP:
                candidate = Position(position.row + 1, position.col)
            else:
                candidate = Position(position.row - 1, position.col)

        if not self.contains(candidate):
            return None
        return candidate

    def opposite_side(self, position: Position, side: Side) -> Side:
        if side == Side.LEFT:
            return Side.RIGHT
        if side == Side.RIGHT:
            return Side.LEFT
        return Side.VERTICAL
#добавление стенки клетке и автоматическое добавление ее же соседу
    def add_wall(self, position: Position, side: Side) -> None:
        if not self.contains(position):
            raise ValueError(f"Клетка стены {position} находится вне лабиринта.")

        self.walls.setdefault(position, set()).add(side)

        neighbor = self.neighbor(position, side)
        if neighbor is not None:
            opposite = self.opposite_side(position, side)
            self.walls.setdefault(neighbor, set()).add(opposite)

    def has_wall(self, position: Position, side: Side) -> bool:
        if self.neighbor(position, side) is None:
            return True
        return side in self.walls.get(position, set())

    def is_exit(self, position: Position, side: Side) -> bool:
        return self.exit_edge.position == position and self.exit_edge.side == side

    def to_dict(self) -> dict:#JSON формат для каждой клетки
        cells: list[dict] = []

        for row in range(self.rows):
            for col in range(self.cols):
                position = Position(row, col)
                walls = [side.value for side in Side if self.has_wall(position, side)]
                cells.append(
                    {
                        "row": row,
                        "col": col,
                        "orientation": self.orientation(position).value,
                        "walls": walls,
                    }
                )

        return {
            "rows": self.rows,
            "cols": self.cols,
            "start": self.start.as_dict(),
            "exit": {
                **self.exit_edge.position.as_dict(),
                "side": self.exit_edge.side.value,
            },
            "lms_radius": self.lms_radius,
            "lms_start_direction": self.lms_start_direction.value,
            "cells": cells,
        }
