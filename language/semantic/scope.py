from __future__ import annotations

from language.semantic.semantic_errors import (
    AmbiguousIdentifierError,
    DuplicateSymbolError,
    UnknownIdentifierError,
)
from language.semantic.symbols import VariableSymbol


class Scope:#область видимости
    def __init__(self, name: str):
        self.name = name
        self.variables: dict[str, VariableSymbol] = {}

    def declare(self, symbol: VariableSymbol) -> None:
        name = symbol.name.lower()

        if name in self.variables:
            raise DuplicateSymbolError(
                f"Имя '{symbol.name}' уже объявлено в области '{self.name}'.",
                symbol.line,
            )

        symbol.name = name
        self.variables[name] = symbol

#по имени определить какая конкретно переменная
    def resolve(self, name: str, line: int | None = None) -> VariableSymbol:
        normalized = name.lower()

        if normalized in self.variables:#сначала полное совпадение
            return self.variables[normalized]

        matches = [#затем , если это сокращение смотрим по началу названий переменных
            symbol
            for full_name, symbol in self.variables.items()
            if full_name.startswith(normalized)
        ]

        if len(matches) == 1:
            return matches[0]

        if len(matches) > 1:#Если найдено более 1 совпадения - некорректное сокращение
            variants = ", ".join(sorted(symbol.name for symbol in matches))
            raise AmbiguousIdentifierError(
                f"Сокращённое имя '{name}' неоднозначно: {variants}.",
                line,
            )

        raise UnknownIdentifierError(
            f"Неизвестная переменная '{name}'.",
            line,
        )
