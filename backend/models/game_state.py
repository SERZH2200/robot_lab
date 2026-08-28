from __future__ import annotations

from dataclasses import dataclass

from backend.models.maze import Maze
from backend.models.robot import RobotState


@dataclass
class GameSnapshot:#"снимок" текцщего состояния игры
    maze: Maze
    robot: RobotState
    completed: bool
    exit_detected: bool
    last_action: str | None = None
    last_result: int | None = None

    def as_dict(self) -> dict:
        return {
            "maze": self.maze.to_dict(),
            "robot": {
                "position": self.robot.position.as_dict(),
                "lms_direction": self.robot.lms_direction.value,
            },
            "completed": self.completed,
            "exit_detected": self.exit_detected,
            "last_action": self.last_action,
            "last_result": self.last_result,
        }
