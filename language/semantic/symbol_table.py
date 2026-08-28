from language.semantic.semantic_errors import (
    DuplicateSymbolError,
    FunctionSemanticError,
)
from language.semantic.symbols import FunctionSymbol


class FunctionTable:
    #Глобальная таблица функций программы
    def __init__(self):
        self.functions: dict[str, FunctionSymbol] = {}

    def declare_function(self, symbol: FunctionSymbol) -> None:#объявление функции, если повторяется название - ошибка
        name = symbol.name.lower()
        if name in self.functions:
            raise DuplicateSymbolError(
                f"Функция '{symbol.name}' уже объявлена.",
                symbol.line,
            )

        symbol.name = name
        self.functions[name] = symbol

    def resolve_function(
        self,
        name: str,
        line: int | None = None,
    ) -> FunctionSymbol:
        normalized = name.lower()
        symbol = self.functions.get(normalized)

        if symbol is None:
            raise FunctionSemanticError(
                f"Неизвестная функция '{name}'.",
                line,
            )

        return symbol
