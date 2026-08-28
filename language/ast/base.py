from dataclasses import dataclass


@dataclass(kw_only=True)
class ASTNode:
    """Базовый класс для всех узлов AST."""
    # Номер строки для семантических и runtime-ошибок.
    line: int | None = None


@dataclass(kw_only=True)
class Expression(ASTNode):
    """Базовый класс для выражений, которые возвращают значение."""
    pass


@dataclass(kw_only=True)
class Statement(ASTNode):
    """Базовый класс для предложений языка."""
    pass


@dataclass(kw_only=True)
class TypeNode(ASTNode):
    """Базовый класс для представления типов языка."""
    pass
