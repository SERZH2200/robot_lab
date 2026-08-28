from __future__ import annotations

from language.ast.base import TypeNode
from language.ast.types import ScalarType, VectorType


SCALAR_TYPES = {"bool", "short", "int"}


def is_scalar(data_type: TypeNode | None) -> bool:
    return isinstance(data_type, ScalarType)


def is_vector(data_type: TypeNode | None) -> bool:
    return isinstance(data_type, VectorType)


def validate_type(data_type: TypeNode) -> bool:
    if isinstance(data_type, ScalarType):
        return data_type.name in SCALAR_TYPES

    if isinstance(data_type, VectorType):
        return validate_type(data_type.element_type)

    return False

#можно ли значение типа actual использовать там где надо expected
def types_compatible(expected: TypeNode | None,actual: TypeNode | None,) -> bool:
    #Неизвестный тип возврата функции проверится позднее во время выполнения
    if expected is None or actual is None:
        return True

    #Все скалярные типы преобразуются друг в друга по правилам языка
    if isinstance(expected, ScalarType) and isinstance(actual, ScalarType):
        return True
    #Векторы проверябтся реккурсивно
    if isinstance(expected, VectorType) and isinstance(actual, VectorType):
        return types_compatible(expected.element_type, actual.element_type)
#Иначе - False
    return False


def type_name(data_type: TypeNode | None) -> str:
    if data_type is None:
        return "неизвестный"

    if isinstance(data_type, ScalarType):
        return data_type.name

    if isinstance(data_type, VectorType):
        return f"vector of {type_name(data_type.element_type)}"

    return type(data_type).__name__


def arithmetic_result_type(
    left: TypeNode | None,
    right: TypeNode | None,
) -> TypeNode | None:
    if left is None or right is None:
        return None

    if not isinstance(left, ScalarType) or not isinstance(right, ScalarType):
        return None

    if left.name == "int" or right.name == "int":
        return ScalarType(name="int")

    return ScalarType(name="short")
