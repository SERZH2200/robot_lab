from dataclasses import dataclass

from .base import Expression


@dataclass
class RobotMove(Expression):
    """Перемещение робота: left, right или vertical."""

    direction: str


@dataclass
class LmsExpression(Expression):
    """Сканирование лазерным дальномером LMS."""

    pass
