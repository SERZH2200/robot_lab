from __future__ import annotations

from threading import RLock

from backend.game.collision import EdgeKind, inspect_edge
from backend.game.movement import movement_result
from backend.game.scanner import scan_horizontal
from backend.models.cell import Side
from backend.models.game_state import GameSnapshot
from backend.models.maze import Maze
from backend.models.robot import RobotState


class GameEngine:
    def __init__(self, maze: Maze):
        self._lock = RLock()#блокировка потока
        self.maze = maze
        self.robot = RobotState(
            position=maze.start,
            lms_direction=maze.lms_start_direction,
        )
        self.completed = False
        self.exit_detected = False
        self.last_action: str | None = None
        self.last_result: int | None = None

    def load_maze(self, maze: Maze) -> None:
        with self._lock:#Замена лабиринта и сброс игры
            self.maze = maze
            self.reset()

    def reset(self) -> None:#сброс игры в начальное состояние
        with self._lock:
            self.robot = RobotState(
                position=self.maze.start,
                lms_direction=self.maze.lms_start_direction,
            )
            self.completed = False
            self.exit_detected = False
            self.last_action = None
            self.last_result = None

    def snapshot(self) -> GameSnapshot:#"Снимок" текущего состояния для frontend
        with self._lock:
            robot_copy = RobotState(
                position=self.robot.position,
                lms_direction=self.robot.lms_direction,
            )
            return GameSnapshot(
                maze=self.maze,
                robot=robot_copy,
                completed=self.completed,
                exit_detected=self.exit_detected,
                last_action=self.last_action,
                last_result=self.last_result,
            )

    def move_left(self) -> int | None:
        return self._move(Side.LEFT)

    def move_right(self) -> int | None:
        return self._move(Side.RIGHT)

    def move_vertical(self) -> int | None:
        return self._move(Side.VERTICAL)

    def _move(self, side: Side) -> int | None:
        with self._lock:
            self.last_action = f"move_{side.value}"

            if self.completed:
                self.last_result = None
                return None

            current = self.robot.position
            edge = inspect_edge(self.maze, current, side)

            if edge.kind == EdgeKind.EXIT:
                self.exit_detected = True
                self.completed = True
                self.last_result = None
                return None

            if edge.kind == EdgeKind.WALL or edge.target is None:
                self.last_result = None
                return None

            result = movement_result(self.maze, current, side)
            self.robot.position = edge.target
            self.last_result = result
            return result

    def lms(self) -> int:
        with self._lock:
            direction = self.robot.lms_direction
            self.last_action = "lms"

            result, exit_detected = scan_horizontal(
                self.maze,
                self.robot.position,
                direction,
                self.maze.lms_radius,
            )

            if exit_detected:
                self.exit_detected = True

            self.robot.lms_direction = (#смена направления LMS
                Side.RIGHT if direction == Side.LEFT else Side.LEFT
            )
            self.last_result = result
            return result
