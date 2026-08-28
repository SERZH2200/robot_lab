class SemanticError(Exception):
    def __init__(self, message: str, line: int | None = None):
        self.message = message
        self.line = line

        if line is None:
            text = message
        else:
            text = f"{message} (строка {line})"

        super().__init__(text)


class DuplicateSymbolError(SemanticError):
    """Повторное объявление имени в одной области видимости"""


class UnknownIdentifierError(SemanticError):
    """Использование неизвестного имени"""


class AmbiguousIdentifierError(SemanticError):
    """Сокращение подходит сразу к нескольким именам"""


class ConstAssignmentError(SemanticError):
    """Попытка изменить константу"""


class TypeMismatchError(SemanticError):
    """Некорректное применение типов"""


class FunctionSemanticError(SemanticError):
    """Ошибка объявления или вызова функции"""


class VectorSemanticError(SemanticError):
    """Ошибка использования vector"""


class EntryPointError(SemanticError):
    """Ошибка точки входа work"""
