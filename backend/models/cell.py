from __future__ import annotations

from enum import Enum


class Side(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    VERTICAL = "vertical"


class TriangleOrientation(str, Enum):
    UP = "up"
    DOWN = "down"
