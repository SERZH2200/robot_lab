from __future__ import annotations

from dataclasses import dataclass

from language.ast.base import TypeNode
from language.runtime.runtime_errors import (
    RuntimeConstError,
    RuntimeTypeError,
    RuntimeVariableError,
)
from language.runtime.values import RuntimeValue, clone_value

#По сути то же что и Scope, только на этапе выполнения
@dataclass
class RuntimeVariable:#Запись о переменной во время выполнения
    name: str
    data_type: TypeNode
    value: RuntimeValue
    is_const: bool = False


class Environment:
    def __init__(self, name: str):
        self.name = name
        self.variables: dict[str, RuntimeVariable] = {}

    def declare(#новая переменная в текущем окружении
        self,
        name: str,
        data_type: TypeNode,
        value: RuntimeValue,
        is_const: bool = False,
        line: int | None = None,
    ) -> None:
        normalized = name.lower()

        if normalized in self.variables:
            raise RuntimeVariableError(
                f"Переменная '{name}' уже существует в '{self.name}'.",
                line,
            )

        self.variables[normalized] = RuntimeVariable(
            name=normalized,
            data_type=data_type,
            value=clone_value(value),
            is_const=is_const,
        )

    def resolve(self, name: str, line: int | None = None) -> RuntimeVariable:#ну и поиск по имени
        normalized = name.lower()
        variable = self.variables.get(normalized)

        if variable is None:
            raise RuntimeVariableError(
                f"Неизвестная переменная '{name}'.",
                line,
            )

        return variable

    def get(self, name: str, line: int | None = None) -> RuntimeValue:
        return self.resolve(name, line).value

    def assign(
        self,
        name: str,
        value: RuntimeValue,
        line: int | None = None,
    ) -> RuntimeValue:
        variable = self.resolve(name, line)

        if variable.is_const:
            raise RuntimeConstError(
                f"Нельзя изменить константу '{variable.name}'.",
                line,
            )

        variable.value = clone_value(value)
        return variable.value
