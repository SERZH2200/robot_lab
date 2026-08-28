from __future__ import annotations

from dataclasses import dataclass, field

from .base import ASTNode, Expression, Statement, TypeNode
from .expressions import VectorInitializer


@dataclass
class VariableDeclarator(ASTNode):
    """Одна переменная внутри объявления: например x set S5."""

    name: str
    initializer: Expression | None = None


@dataclass
class VectorDeclarator(ASTNode):
    """Один vector с необязательным размером и инициализатором."""

    name: str
    size: Expression | None = None
    initializer: VectorInitializer | None = None


@dataclass
class VariableDeclaration(Statement):
    """Объявление одной или нескольких переменных одного типа."""

    data_type: TypeNode
    variables: list[VariableDeclarator | VectorDeclarator] = field(default_factory=list)
    is_const: bool = False
