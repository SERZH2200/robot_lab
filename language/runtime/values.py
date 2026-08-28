from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from language.ast.base import TypeNode
from language.ast.types import ScalarType, VectorType


class BoolState(Enum):
    FALSE = -1
    UNDEFINED = 0
    TRUE = 1


@dataclass
class RuntimeValue:
    pass


@dataclass
class BoolValue(RuntimeValue):
    value: BoolState


@dataclass
class ShortValue(RuntimeValue):
    value: int


@dataclass
class IntValue(RuntimeValue):
    value: int


@dataclass
class VectorValue(RuntimeValue):
    elements: list[RuntimeValue]

#глубокая копия для передачи по значению
def clone_value(value: RuntimeValue) -> RuntimeValue:
    if isinstance(value, BoolValue):
        return BoolValue(value.value)

    if isinstance(value, ShortValue):
        return ShortValue(value.value)

    if isinstance(value, IntValue):
        return IntValue(value.value)

    if isinstance(value, VectorValue):
        return VectorValue([clone_value(element) for element in value.elements])

    raise TypeError(f"Неизвестный runtime-тип {type(value).__name__}.")


def bool_to_int(value: BoolValue) -> int:
    return value.value.value


def int_to_bool(value: int) -> BoolValue:
    if value < 0:
        return BoolValue(BoolState.FALSE)

    if value > 0:
        return BoolValue(BoolState.TRUE)

    return BoolValue(BoolState.UNDEFINED)


def to_int(value: RuntimeValue) -> int:
    if isinstance(value, BoolValue):
        return bool_to_int(value)

    if isinstance(value, (ShortValue, IntValue)):
        return value.value

    raise TypeError("Vector нельзя преобразовать в арифметическое значение.")


def to_bool(value: RuntimeValue) -> BoolValue:
    if isinstance(value, BoolValue):
        return BoolValue(value.value)

    if isinstance(value, (ShortValue, IntValue)):
        return int_to_bool(value.value)

    raise TypeError("Vector нельзя преобразовать в bool.")


def default_value(data_type: TypeNode) -> RuntimeValue:
    if isinstance(data_type, ScalarType):
        if data_type.name == "bool":
            return BoolValue(BoolState.UNDEFINED)

        if data_type.name == "short":
            return ShortValue(0)

        if data_type.name == "int":
            return IntValue(0)

    if isinstance(data_type, VectorType):
        return VectorValue([])

    raise TypeError(f"Неизвестный тип {type(data_type).__name__}.")
