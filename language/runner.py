from __future__ import annotations

import argparse
from pathlib import Path

from language.lexer.lex_err import LexerError
from language.lexer.lexer import build_lexer
from language.parser.parser import build_parser
from language.parser.parser_errors import ParserError
from language.runtime.interpreter import Interpreter
from language.runtime.robot import RobotController
from language.runtime.runtime_errors import RuntimeLanguageError
from language.runtime.values import (
    BoolState,
    BoolValue,
    IntValue,
    RuntimeValue,
    ShortValue,
    VectorValue,
)
from language.semantic.analyzer import SemanticAnalyzer
from language.semantic.semantic_errors import SemanticError


def build_program(source: str):
    lexer = build_lexer()
    lexer.lineno = 1
    parser = build_parser()

    program = parser.parse(source, lexer=lexer)

    if program is None:
        raise ParserError("Не удалось построить программу.")

    return SemanticAnalyzer().analyze(program)


def run_source(
    source: str,
    robot: RobotController | None = None,
) -> RuntimeValue:
    program = build_program(source)
    interpreter = Interpreter(program, robot)
    return interpreter.run()


def run_file(
    path: str | Path,
    robot: RobotController | None = None,
) -> RuntimeValue:
    source_path = Path(path)
    source = source_path.read_text(encoding="utf-8")
    return run_source(source, robot)


def format_value(value: RuntimeValue) -> str:
    if isinstance(value, BoolValue):
        if value.value == BoolState.TRUE:
            return "true"
        if value.value == BoolState.FALSE:
            return "false"
        return "undefined"

    if isinstance(value, (ShortValue, IntValue)):
        return str(value.value)

    if isinstance(value, VectorValue):
        return "{" + ", ".join(format_value(element) for element in value.elements) + "}"

    return str(value)


def main() -> None:
    argument_parser = argparse.ArgumentParser(
        description="Запуск программы на языке клеточного робота."
    )
    argument_parser.add_argument(
        "program",
        help="Путь к .robot файлу.",
    )
    argument_parser.add_argument(
        "--mock-robot",
        action="store_true",
        help="Подключить тестового робота для move и lms.",
    )

    args = argument_parser.parse_args()

    robot = None
    if args.mock_robot:
        from language.robot.mock_robot import MockRobot
        robot = MockRobot()

    try:
        result = run_file(args.program, robot)
    except (LexerError, ParserError, SemanticError, RuntimeLanguageError, OSError) as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error

    print(f"Программа завершилас. work() вернул: {format_value(result)}")


if __name__ == "__main__":
    main()
