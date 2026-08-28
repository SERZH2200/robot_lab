from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BackendConfig:
    project_root: Path
    maze_dir: Path
    default_maze: str = "demo.txt"


def load_config() -> BackendConfig:
    project_root = Path(__file__).resolve().parent.parent
    return BackendConfig(
        project_root=project_root,
        maze_dir=project_root / "mazes",
    )
