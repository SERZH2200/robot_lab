from __future__ import annotations

from language.ast.base import TypeNode
from language.ast.types import ScalarType, VectorType
from language.runtime.arithmetic import SHORT_MAX, SHORT_MIN, INT_MAX, INT_MIN
from language.runtime.runtime_errors import RuntimeTypeError, RuntimeVectorError
from language.runtime.values import (
    BoolValue,
    IntValue,
    RuntimeValue,
    ShortValue,
    VectorValue,
    clone_value,
    default_value,
    int_to_bool,
    to_int,
)


BOOL_SIZE = 1
SHORT_SIZE = 2
INT_SIZE = 4


def get_index(value: RuntimeValue, line: int | None = None) -> int:
    try:
        return to_int(value)
    except TypeError as error:
        raise RuntimeVectorError(
            "Индекс vector должен быть скалярным.",
            line,
        ) from error


def get_element(
    vector: VectorValue,
    index: int,
    line: int | None = None,
) -> RuntimeValue:
    if index < 0 or index >= len(vector.elements):
        raise RuntimeVectorError(
            f"Индекс {index} выходит за границы vector размером {len(vector.elements)}.",
            line,
        )

    return vector.elements[index]


def set_element(
    vector: VectorValue,
    index: int,
    value: RuntimeValue,
    line: int | None = None,
) -> RuntimeValue:
    if index < 0 or index >= len(vector.elements):
        raise RuntimeVectorError(
            f"Индекс {index} выходит за границы vector размером {len(vector.elements)}.",
            line,
        )

    vector.elements[index] = clone_value(value)
    return vector.elements[index]


def convert_value(
    value: RuntimeValue,
    target_type: TypeNode,
    line: int | None = None,
) -> RuntimeValue:
    if isinstance(target_type, ScalarType):
        if target_type.name == "bool":
            if isinstance(value, VectorValue):
                raise RuntimeTypeError(
                    "Vector нельзя преобразовать в bool.",
                    line,
                )

            return int_to_bool(to_int(value))

        if target_type.name == "short":
            if isinstance(value, VectorValue):
                raise RuntimeTypeError(
                    "Vector нельзя преобразовать в short.",
                    line,
                )

            number = to_int(value)

            if number < SHORT_MIN or number > SHORT_MAX:
                raise RuntimeTypeError(
                    f"Значение {number} не помещается в short.",
                    line,
                )

            return ShortValue(number)

        if target_type.name == "int":
            if isinstance(value, VectorValue):
                raise RuntimeTypeError(
                    "Vector нельзя преобразовать в int.",
                    line,
                )

            number = to_int(value)

            if number < INT_MIN or number > INT_MAX:
                raise RuntimeTypeError(
                    f"Значение {number} не помещается в int.",
                    line,
                )

            return IntValue(number)

    if isinstance(target_type, VectorType):
        if not isinstance(value, VectorValue):
            raise RuntimeTypeError(
                "Ожидалось значение типа vector.",
                line,
            )

        return VectorValue(
            [
                convert_value(element, target_type.element_type, line)
                for element in value.elements
            ]
        )

    raise RuntimeTypeError(
        f"Неизвестный тип {type(target_type).__name__}.",
        line,
    )


def make_sized_vector(
    element_type: TypeNode,
    size: int,
    line: int | None = None,
) -> VectorValue:
    if size < 0:
        raise RuntimeVectorError(
            "Размер vector не может быть отрицательным.",
            line,
        )

    return VectorValue(
        [clone_value(default_value(element_type)) for _ in range(size)]
    )


def type_size(data_type: TypeNode, line: int | None = None) -> int:#sizeof типа
    if isinstance(data_type, ScalarType):
        if data_type.name == "bool":
            return BOOL_SIZE

        if data_type.name == "short":
            return SHORT_SIZE

        if data_type.name == "int":
            return INT_SIZE

    if isinstance(data_type, VectorType):
        raise RuntimeTypeError(
            "vector нельзя использовать как непосредственный тип в sizeof.",
            line,
        )

    raise RuntimeTypeError(
        f"Невозможно определить sizeof для {type(data_type).__name__}.",
        line,
    )


def value_size(value: RuntimeValue) -> int:#sizeof конкретного перемренного
    if isinstance(value, BoolValue):
        return BOOL_SIZE

    if isinstance(value, ShortValue):
        return SHORT_SIZE

    if isinstance(value, IntValue):
        return INT_SIZE

    if isinstance(value, VectorValue):
        return sum(value_size(element) for element in value.elements)

    raise TypeError(f"Неизвестный runtime-тип {type(value).__name__}.")
