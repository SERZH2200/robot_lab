from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class MockRobot:
    left_results: deque[int | None] = field(default_factory=deque)
    right_results: deque[int | None] = field(default_factory=deque)
    vertical_results: deque[int | None] = field(default_factory=deque)
    lms_results: deque[int] = field(default_factory=deque)
    commands: list[str] = field(default_factory=list)

    def move_left(self) -> int | None:
        self.commands.append("left")
        if self.left_results:
            return self.left_results.popleft()
        return -1

    def move_right(self) -> int | None:
        self.commands.append("right")
        if self.right_results:
            return self.right_results.popleft()
        return 1

    def move_vertical(self) -> int | None:
        self.commands.append("vertical")
        if self.vertical_results:
            return self.vertical_results.popleft()
        return 1

    def lms(self) -> int:
        self.commands.append("lms")
        if self.lms_results:
            return self.lms_results.popleft()
        return 0
