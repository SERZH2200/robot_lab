from dataclasses import dataclass, field

from .base import ASTNode, Expression, TypeNode
from .statements import Block


@dataclass
class Parameter(ASTNode):
    """Параметр функции: тип и имя."""

    data_type: TypeNode
    name: str


@dataclass
class FunctionDefinition(ASTNode):
    """Описание функции языка."""

    name: str
    parameters: list[Parameter]
    body: Block
    return_expression: Expression


@dataclass
class Program(ASTNode):
    """Корневой узел AST всей программы."""

    functions: list[FunctionDefinition] = field(default_factory=list)
