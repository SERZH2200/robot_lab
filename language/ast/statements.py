from __future__ import annotations

from dataclasses import dataclass, field

from .base import Expression, Statement


@dataclass
class Block(Statement):
    """Группа предложений между begin и end."""

    statements: list[Statement] = field(default_factory=list)


@dataclass
class ExpressionStatement(Statement):
    """Выражение, использованное как отдельное предложение."""

    expression: Expression


@dataclass
class IfStatement(Statement):
    """Условный оператор if ... then ... else ... ."""

    condition: Expression
    then_branch: Statement
    else_branch: Statement


@dataclass
class DoWhileStatement(Statement):
    """Цикл do ... while ... ."""

    body: Statement
    condition: Expression
