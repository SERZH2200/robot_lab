from __future__ import annotations

from pathlib import Path

from backend.models.cell import Side
from backend.models.maze import ExitEdge, Maze
from backend.models.position import Position


class MazeFormatError(ValueError):
    pass


def _side(value: str, line_number: int) -> Side:
    try:
        return Side(value.lower())
    except ValueError as error:
        raise MazeFormatError(
            f"Строка {line_number}: неизвестная сторона '{value}'."
        ) from error

#парсинг текстового файла с описанием лабиринта
def load_maze(path: str | Path) -> Maze:
    source_path = Path(path)
    lines = source_path.read_text(encoding="utf-8").splitlines()

    rows: int | None = None
    cols: int | None = None
    start: Position | None = None
    exit_edge: ExitEdge | None = None
    lms_radius = 5
    lms_start_direction = Side.LEFT
    walls: list[tuple[Position, Side]] = []

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        parts = line.split()
        command = parts[0].lower()

        try:
            if command == "size":
                if len(parts) != 3:
                    raise MazeFormatError(f"Строка {line_number}: ожидается 'size <rows> <cols>'.")
                rows = int(parts[1])
                cols = int(parts[2])

            elif command == "start":
                if len(parts) != 3:
                    raise MazeFormatError(f"Строка {line_number}: ожидается 'start <row> <col>'.")
                start = Position(int(parts[1]), int(parts[2]))

            elif command == "exit":
                if len(parts) != 4:
                    raise MazeFormatError(
                        f"Строка {line_number}: ожидается 'exit <row> <col> <left|right|vertical>'."
                    )
                exit_edge = ExitEdge(
                    Position(int(parts[1]), int(parts[2])),
                    _side(parts[3], line_number),
                )

            elif command == "wall":
                if len(parts) != 4:
                    raise MazeFormatError(
                        f"Строка {line_number}: ожидается 'wall <row> <col> <left|right|vertical>'."
                    )
                walls.append(
                    (
                        Position(int(parts[1]), int(parts[2])),
                        _side(parts[3], line_number),
                    )
                )

            elif command == "lms_radius":
                if len(parts) != 2:
                    raise MazeFormatError(f"Строка {line_number}: ожидается 'lms_radius <число>'.")
                lms_radius = int(parts[1])

            elif command == "lms_start":
                if len(parts) != 2:
                    raise MazeFormatError(f"Строка {line_number}: ожидается 'lms_start <left|right>'.")
                lms_start_direction = _side(parts[1], line_number)
                if lms_start_direction == Side.VERTICAL:
                    raise MazeFormatError(f"Строка {line_number}: LMS не может начинать с vertical.")

            else:
                raise MazeFormatError(
                    f"Строка {line_number}: неизвестная директива '{parts[0]}'."
                )

        except ValueError as error:
            if isinstance(error, MazeFormatError):
                raise
            raise MazeFormatError(
                f"Строка {line_number}: некорректное числовое значение."
            ) from error

    if rows is None or cols is None:
        raise MazeFormatError("Не задан размер лабиринта директивой size.")

    if start is None:
        raise MazeFormatError("Не задана начальная позиция робота директивой start.")

    if exit_edge is None:
        raise MazeFormatError("Не задан выход директивой exit.")

    maze = Maze(#сначала создаем лабиринт, в нем проверяется геометрия и только потом
        rows=rows,
        cols=cols,
        start=start,
        exit_edge=exit_edge,
        lms_radius=lms_radius,
        lms_start_direction=lms_start_direction,
    )

    for position, side in walls:#добавляем стены
        maze.add_wall(position, side)

    return maze
