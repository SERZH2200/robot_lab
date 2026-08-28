from typing import Protocol

#Интерфейс между интерпретатором языка и реализацией робота
class RobotController(Protocol):
    def move_left(self) -> int | None:
        ...

    def move_right(self) -> int | None:
        ...

    def move_vertical(self) -> int | None:
        ...

    def lms(self) -> int:
        ...
