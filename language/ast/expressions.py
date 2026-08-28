from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import ASTNode, Expression, TypeNode


@dataclass
class Literal(Expression):
    """Литерал языка: int, short, true, false или undefined."""

    literal_type: str
    value: Any


@dataclass
class Variable(Expression):
    """Обращение к переменной по имени."""

    name: str


@dataclass
class BinaryOperation(Expression):
    """Бинарная операция: add, sub, сравнение, and/or и т.д."""

    operator: str
    left: Expression
    right: Expression


@dataclass
class Assignment(Expression):
    """Присваивание. Является выражением из-за правоассоциативного set."""

    target: Variable | ArrayAccess
    value: Expression


@dataclass
class ArrayAccess(Expression):
    """Доступ к элементу массива. Вложенность строится рекурсивно."""

    array: Variable | ArrayAccess
    index: Expression


@dataclass
class Sizeof(Expression):
    """Оператор sizeof для типа или переменной."""

    target_kind: str
    target: TypeNode | str


@dataclass
class FunctionCall(Expression):
    """Вызов функции. По ТЗ аргументы являются именами переменных."""

    name: str
    arguments: list[Variable] = field(default_factory=list)


@dataclass
class VectorInitializer(ASTNode):
    """Инициализатор vector, в том числе вложенный: {{...}, {...}}."""

    values: list[Expression | VectorInitializer] = field(default_factory=list)
