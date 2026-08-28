from __future__ import annotations

from collections.abc import Callable

from backend.game.engine import GameEngine

#Адаптер между RobotController и GameEngine
class GameRobotAdapter:
    def __init__(
        self,
        engine: GameEngine,
        on_state_change: Callable[[dict], None] | None = None,
    ):
        self.engine = engine
        self.on_state_change = on_state_change

    def _notify(self) -> None:#Отправляет сообщения об изменении состояния, вызывается при каждом действии
        if self.on_state_change is not None:
            self.on_state_change(self.engine.snapshot().as_dict())

    def move_left(self) -> int | None:
        result = self.engine.move_left()
        self._notify()
        return result

    def move_right(self) -> int | None:
        result = self.engine.move_right()
        self._notify()
        return result

    def move_vertical(self) -> int | None:
        result = self.engine.move_vertical()
        self._notify()
        return result

    def lms(self) -> int:
        result = self.engine.lms()
        self._notify()
        return result
