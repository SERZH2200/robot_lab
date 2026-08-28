from __future__ import annotations

from dataclasses import dataclass

#Координаты клетки: строка и столбец
@dataclass(frozen=True, slots=True)#slots=true для фиксированной структуры, а также оптимизации
class Position:
    row: int
    col: int

    def as_dict(self) -> dict[str, int]:#Position в JSON формате
        return {
            "row": self.row,
            "col": self.col,
        }
