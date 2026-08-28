from __future__ import annotations

from dataclasses import dataclass

from language.ast.base import TypeNode
from language.ast.functions import FunctionDefinition, Parameter


@dataclass
class VariableSymbol:#Описание переменной в таблице символов
    name: str
    data_type: TypeNode
    is_const: bool = False
    is_parameter: bool = False
    line: int | None = None
    static_size: int | None = None#Проверка на выход за границу, если размер зависит от переменной - в runtime уже


@dataclass
class FunctionSymbol:#запись о функции в таблице функций

    name: str
    parameters: list[Parameter]
    node: FunctionDefinition#ссылка на объект ф-ии
    return_type: TypeNode | None = None
    line: int | None = None#строка объявления ф-ии
