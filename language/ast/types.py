from dataclasses import dataclass

from .base import TypeNode


@dataclass
class ScalarType(TypeNode):
    """Скалярный тип: bool, short или int."""

    name: str


@dataclass
class VectorType(TypeNode):
    """Тип vector. element_type может сам быть VectorType."""

    element_type: TypeNode
