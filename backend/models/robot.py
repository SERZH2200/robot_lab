from __future__ import annotations

from dataclasses import dataclass

from backend.models.cell import Side
from backend.models.position import Position


@dataclass
class RobotState:
    position: Position
    lms_direction: Side = Side.LEFT
