from __future__ import annotations

from language.runtime.runtime_errors import RuntimeOverflowError
from language.runtime.values import (
    RuntimeValue,
    ShortValue,
    IntValue,
    to_int,
)


SHORT_MIN = -(2 ** 15)
SHORT_MAX = 2 ** 15 - 1

INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1


def _make_numeric_result(
    value: int,
    force_int: bool = False,
    line: int | None = None,
) -> RuntimeValue:
    #Операция с int всегда возвращает int, обратного сужения нет
    if force_int:
        if INT_MIN <= value <= INT_MAX:
            return IntValue(value)

        raise RuntimeOverflowError(
            "Переполнение разрядной сетки int.",
            line,
        )
    #Операция над short/bool сначала выполняется в сетке short
    if SHORT_MIN <= value <= SHORT_MAX:
        return ShortValue(value)

    #При переполнении short результат расширяется до int
    if INT_MIN <= value <= INT_MAX:
        return IntValue(value)

    raise RuntimeOverflowError(
        "Переполнение разрядной сетки int.",
        line,
    )


def add(
    left: RuntimeValue,
    right: RuntimeValue,
    line: int | None = None,
) -> RuntimeValue:
    left_value = to_int(left)
    right_value = to_int(right)

    result = left_value + right_value
    force_int = isinstance(left, IntValue) or isinstance(right, IntValue)

    return _make_numeric_result(result, force_int, line)


def sub(
    left: RuntimeValue,
    right: RuntimeValue,
    line: int | None = None,
) -> RuntimeValue:
    left_value = to_int(left)
    right_value = to_int(right)

    result = left_value - right_value
    force_int = isinstance(left, IntValue) or isinstance(right, IntValue)

    return _make_numeric_result(result, force_int, line)