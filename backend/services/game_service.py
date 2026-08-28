from __future__ import annotations

from pathlib import Path

from backend.game.engine import GameEngine
from backend.game.maze_loader import load_maze


class GameService:
    def __init__(self, maze_dir: Path, default_maze: str):
        self.maze_dir = maze_dir.resolve()
        self.current_maze_name = default_maze
        self.engine = GameEngine(self._load(default_maze))

    def _maze_path(self, maze_name: str) -> Path:
        candidate = (self.maze_dir / maze_name).resolve()

        if self.maze_dir not in candidate.parents:
            raise ValueError("Недопустимый путь к файлу лабиринта.")

        return candidate

    def _load(self, maze_name: str):
        path = self._maze_path(maze_name)
        if not path.is_file():
            raise FileNotFoundError(f"Лабиринт '{maze_name}' не найден.")
        return load_maze(path)

    def load(self, maze_name: str) -> dict:
        maze = self._load(maze_name)
        self.engine.load_maze(maze)
        self.current_maze_name = maze_name
        return self.state()

    def state(self) -> dict:#JSON представление текущего состояния
        result = self.engine.snapshot().as_dict()
        result["maze_name"] = self.current_maze_name
        return result

    def reset(self) -> dict:
        self.engine.reset()
        return self.state()

    def move(self, direction: str) -> tuple[int | None, dict]:#получает строчку и обращется к движку
        normalized = direction.lower()

        if normalized == "left":
            result = self.engine.move_left()
        elif normalized == "right":
            result = self.engine.move_right()
        elif normalized in {"vertical", "move"}:
            result = self.engine.move_vertical()
        else:
            raise ValueError(f"Неизвестное направление '{direction}'.")

        return result, self.state()

    def lms(self) -> tuple[int, dict]:
        result = self.engine.lms()
        return result, self.state()

    def list_mazes(self) -> list[str]:
        if not self.maze_dir.exists():
            return []
        return sorted(path.name for path in self.maze_dir.glob("*.txt") if path.is_file())
