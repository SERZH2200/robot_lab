from __future__ import annotations

from language.ast.base import Expression, Statement, TypeNode
from language.ast.declarations import (
    VariableDeclaration,
    VariableDeclarator,
    VectorDeclarator,
)
from language.ast.expressions import (
    ArrayAccess,
    Assignment,
    BinaryOperation,
    FunctionCall,
    Literal,
    Sizeof,
    Variable,
    VectorInitializer,
)
from language.ast.functions import FunctionDefinition, Program
from language.ast.robot_commands import LmsExpression, RobotMove
from language.ast.statements import (
    Block,
    DoWhileStatement,
    ExpressionStatement,
    IfStatement,
)
from language.ast.types import ScalarType, VectorType
from language.semantic.scope import Scope
from language.semantic.semantic_errors import (
    ConstAssignmentError,
    EntryPointError,
    FunctionSemanticError,
    SemanticError,
    TypeMismatchError,
    VectorSemanticError,
)
from language.semantic.symbol_table import FunctionTable
from language.semantic.symbols import FunctionSymbol, VariableSymbol
from language.semantic.type_system import (
    arithmetic_result_type,
    is_scalar,
    type_name,
    types_compatible,
    validate_type,
)


class SemanticAnalyzer:
    #Проверка AST перед передачей программы интерпретатору

    def __init__(self):
        self.symbol_table = FunctionTable()

    def analyze(self, program: Program) -> Program:
        self.symbol_table = FunctionTable()#очистка таблицы, чтобы можно было один анализатор для двух программ использовать
        self._register_functions(program)#все функции предварительно регистрируем в таблице
        self._check_entry_point()#Проверка наличия точки входа - work()

        #Несколько проходов позволяют вывести типы функций,
        #которые вызывают функции, объявленные ниже по тексту
        for _ in range(len(program.functions) + 1):#функции могут вызывать друг друга, поэтому необходимо
            #len(program.functions) + 1 проходов для установления возвращаемых типов
            changed = False

            for function in program.functions:
                inferred = self._analyze_function(function)#получаем предполагаемый тип return'а
                symbol = self.symbol_table.resolve_function(function.name,function.line)

                if symbol.return_type is None and inferred is not None:
                    symbol.return_type = inferred
                    changed = True
                elif (
                    symbol.return_type is not None
                    and inferred is not None
                    and not types_compatible(symbol.return_type, inferred)
                ):
                    raise TypeMismatchError(
                        f"Тип возвращаемого значения функции '{function.name}' изменяется между анализами.",
                        function.return_expression.line,
                    )

            if not changed:
                break

        # Финальный проход выполняет проверки уже с максимально известными
        # возвращаемыми типами функций.
        for function in program.functions:
            self._analyze_function(function)

        return program

    def _register_functions(self, program: Program) -> None:#заполнение таблицы функций
        for function in program.functions:
            self.symbol_table.declare_function(
                FunctionSymbol(
                    name=function.name,
                    parameters=function.parameters,
                    node=function,
                    line=function.line,
                )
            )

    def _check_entry_point(self) -> None:
        if "work" not in self.symbol_table.functions:
            raise EntryPointError(
                "В программе отсутствует точка входа 'work'."
            )
        work_function = self.symbol_table.functions["work"]

        if work_function.parameters:
            raise EntryPointError(
                "Функция 'work' не должна иметь параметров."
            )

    def _analyze_function(self,function: FunctionDefinition,) -> TypeNode | None:
        scope = Scope(function.name)

        for parameter in function.parameters:
            self._ensure_valid_type(parameter.data_type, parameter.line)
            scope.declare(
                VariableSymbol(
                    name=parameter.name,
                    data_type=parameter.data_type,
                    is_parameter=True,
                    line=parameter.line,
                )
            )

        self._analyze_block(function.body, scope)
        return self._infer_expression(function.return_expression, scope)

    def _analyze_block(self, block: Block, scope: Scope) -> None:
        for statement in block.statements:
            self._analyze_statement(statement, scope)

    #Определение вида предложения и запуск соответствующей семантической проверки
    def _analyze_statement(self, statement: Statement, scope: Scope) -> None:
        if isinstance(statement, VariableDeclaration):
            self._analyze_declaration(statement, scope)
            return

        if isinstance(statement, ExpressionStatement):
            self._infer_expression(statement.expression, scope)
            return

        if isinstance(statement, IfStatement):
            condition_type = self._infer_expression(statement.condition, scope)
            self._require_scalar(#проверка, что условие не вектор
                condition_type,
                statement.condition.line,
                "Условие if",
            )
            self._analyze_statement(statement.then_branch, scope)
            self._analyze_statement(statement.else_branch, scope)
            return

        if isinstance(statement, DoWhileStatement):
            self._analyze_statement(statement.body, scope)
            condition_type = self._infer_expression(statement.condition, scope)
            self._require_scalar(
                condition_type,
                statement.condition.line,
                "Условие while",
            )
            return

        if isinstance(statement, Block):
            self._analyze_block(statement, scope)
            return

        raise SemanticError(
            f"Неизвестный тип предложения {type(statement).__name__}.",
            statement.line,
        )

    def _analyze_declaration(#выбор проверки для scalar/vector
        self,
        declaration: VariableDeclaration,
        scope: Scope,
    ) -> None:
        self._ensure_valid_type(declaration.data_type, declaration.line)

        for declarator in declaration.variables:
            if isinstance(declarator, VariableDeclarator):
                self._analyze_scalar_declarator(declaration,declarator,scope)
                continue

            if isinstance(declarator, VectorDeclarator):
                self._analyze_vector_declarator(
                    declaration,
                    declarator,
                    scope,
                )
                continue

            raise SemanticError(
                f"Неизвестный тип объявления {type(declarator).__name__}.",
                declarator.line,
            )

    def _analyze_scalar_declarator(
        self,
        declaration: VariableDeclaration,
        declarator: VariableDeclarator,
        scope: Scope,
    ) -> None:
        if isinstance(declaration.data_type, VectorType):
            raise TypeMismatchError(
                "Для типа vector ожидается объявление массива.",
                declarator.line,
            )

        if declarator.initializer is not None:
            initializer_type = self._infer_expression(
                declarator.initializer,
                scope,
            )
            self._require_compatible(
                declaration.data_type,
                initializer_type,
                declarator.line,
                f"Инициализация переменной '{declarator.name}'",
            )

        scope.declare(#обеспечивает проверку использования до объявления.
            VariableSymbol(
                name=declarator.name,
                data_type=declaration.data_type,
                is_const=declaration.is_const,
                line=declarator.line,
            )
        )

    def _analyze_vector_declarator(#Проверка размера, инициализатора и типа объявляемого vector
        self,
        declaration: VariableDeclaration,
        declarator: VectorDeclarator,
        scope: Scope,
    ) -> None:
        if not isinstance(declaration.data_type, VectorType):
            raise VectorSemanticError(
                f"'{declarator.name}' объявлен как массив без типа vector.",
                declarator.line,
            )

        static_size = None

        if declarator.size is not None:
            size_type = self._infer_expression(declarator.size, scope)
            self._require_scalar(
                size_type,
                declarator.size.line,
                "Размер vector",
            )
            static_size = self._static_integer(declarator.size)#вычисление размера типа s2 add s3

            if static_size is not None and static_size < 0:
                raise VectorSemanticError(
                    f"Размер vector '{declarator.name}' не может быть отрицательным.",
                    declarator.size.line,
                )

        if declarator.initializer is not None:
            self._validate_vector_initializer(
                declarator.initializer,
                declaration.data_type,
                scope,
            )

            if static_size is None and declarator.size is None:
                static_size = len(declarator.initializer.values)

            if (
                static_size is not None
                and declarator.size is not None
                and static_size != len(declarator.initializer.values)
            ):
                raise VectorSemanticError(
                    f"Размер vector '{declarator.name}' равен {static_size}, "
                    f"но инициализатор содержит {len(declarator.initializer.values)} элементов.",
                    declarator.line,
                )

        scope.declare(
            VariableSymbol(
                name=declarator.name,
                data_type=declaration.data_type,
                is_const=declaration.is_const,
                line=declarator.line,
                static_size=static_size,
            )
        )

    def _validate_vector_initializer(#Рекурсивная проверка типов элементов и вложенности инициализатора vector
        self,
        initializer: VectorInitializer,
        vector_type: VectorType,
        scope: Scope,
    ) -> None:
        element_type = vector_type.element_type

        for value in initializer.values:
            if isinstance(value, VectorInitializer):
                if not isinstance(element_type, VectorType):
                    raise VectorSemanticError(
                        "Вложенный инициализатор допустим только для вложенного vector.",
                        value.line,
                    )

                self._validate_vector_initializer(
                    value,
                    element_type,
                    scope,
                )
                continue

            actual_type = self._infer_expression(value, scope)

            self._require_compatible(
                element_type,
                actual_type,
                value.line,
                "Элемент инициализатора vector",
            )

    def _infer_expression(#какой тип имеет выражение
        self,
        expression: Expression,
        scope: Scope,
    ) -> TypeNode | None:
        if isinstance(expression, Literal):
            return self._literal_type(expression)

        if isinstance(expression, Variable):
            symbol = scope.resolve(expression.name, expression.line)
            expression.name = symbol.name
            return symbol.data_type

        if isinstance(expression, BinaryOperation):
            return self._infer_binary_operation(expression, scope)

        if isinstance(expression, Assignment):
            target_type = self._infer_lvalue(expression.target, scope)
            value_type = self._infer_expression(expression.value, scope)
            self._require_compatible(
                target_type,
                value_type,
                expression.line,
                "Присваивание",
            )
            return target_type

        if isinstance(expression, ArrayAccess):
            return self._infer_array_access(expression, scope)

        if isinstance(expression, Sizeof):
            if expression.target_kind == "type":
                if not isinstance(expression.target, ScalarType):
                    raise TypeMismatchError(
                        "sizeof не принимает vector в качестве типа.",
                        expression.line,
                    )
                self._ensure_valid_type(expression.target, expression.line)
            else:
                symbol = scope.resolve(str(expression.target), expression.line)
                expression.target = symbol.name

            return ScalarType(name="int", line=expression.line)

        if isinstance(expression, FunctionCall):
            return self._infer_function_call(expression, scope)

        if isinstance(expression, RobotMove):
            return ScalarType(name="short", line=expression.line)

        if isinstance(expression, LmsExpression):
            return ScalarType(name="int", line=expression.line)

        raise SemanticError(
            f"Неизвестный тип выражения {type(expression).__name__}.",
            expression.line,
        )

    def _infer_binary_operation(
        self,
        expression: BinaryOperation,
        scope: Scope,
    ) -> TypeNode | None:
        left_type = self._infer_expression(expression.left, scope)
        right_type = self._infer_expression(expression.right, scope)
#бинарные операции только для скаляров
        self._require_scalar(
            left_type,
            expression.left.line,
            f"Левый операнд '{expression.operator}'",
        )
        self._require_scalar(
            right_type,
            expression.right.line,
            f"Правый операнд '{expression.operator}'",
        )

        if expression.operator in {"add", "sub"}:
            return arithmetic_result_type(left_type, right_type)

        if expression.operator in {
            "first_smaller",
            "first_larger",
            "second_smaller",
            "second_larger",
            "and",
            "or",
            "not_and",
            "not_or",
        }:
            return ScalarType(name="bool", line=expression.line)

        raise SemanticError(
            f"Неизвестный оператор '{expression.operator}'.",
            expression.line,
        )

    def _infer_lvalue(
        self,
        target: Variable | ArrayAccess,
        scope: Scope,
    ) -> TypeNode | None:
        root = self._root_variable(target)
        symbol = scope.resolve(root.name, root.line)
        root.name = symbol.name

        if symbol.is_const:
            raise ConstAssignmentError(
                f"Нельзя изменить константу '{symbol.name}'.",
                target.line,
            )

        if isinstance(target, Variable):
            return symbol.data_type

        return self._infer_array_access(target, scope)

    def _infer_array_access(
        self,
        access: ArrayAccess,
        scope: Scope,
    ) -> TypeNode | None:
        if isinstance(access.array, Variable):
            symbol = scope.resolve(access.array.name, access.array.line)
            access.array.name = symbol.name
            array_type = symbol.data_type

            index_value = self._static_integer(access.index)
            if ( symbol.static_size is not None and index_value is not None and not 0 <= index_value < symbol.static_size):
                raise VectorSemanticError(
                    f"Индекс {index_value} выходит за границы vector '{symbol.name}' "
                    f"размера {symbol.static_size}.",
                    access.index.line,
                )
        else:
            array_type = self._infer_array_access(access.array, scope)

        index_type = self._infer_expression(access.index, scope)
        self._require_scalar(
            index_type,
            access.index.line,
            "Индекс vector",
        )

        if array_type is None:
            return None

        if not isinstance(array_type, VectorType):
            raise VectorSemanticError(
                f"Индексация применяется только к vector, получен тип {type_name(array_type)}.",
                access.line,
            )

        return array_type.element_type

    def _infer_function_call(
        self,
        call: FunctionCall,
        scope: Scope,
    ) -> TypeNode | None:
        function = self.symbol_table.resolve_function(call.name, call.line)
        call.name = function.name

        if len(call.arguments) != len(function.parameters):
            raise FunctionSemanticError(
                f"Функция '{call.name}' ожидает {len(function.parameters)} аргументов, "
                f"получено {len(call.arguments)}.",
                call.line,
            )

        for argument, parameter in zip(call.arguments, function.parameters):#сопоставление аргументов и параметров
            symbol = scope.resolve(argument.name, argument.line)
            argument.name = symbol.name

            self._require_compatible(
                parameter.data_type,
                symbol.data_type,
                argument.line,
                f"Аргумент '{argument.name}' функции '{call.name}'",
            )

        return function.return_type

    def _literal_type(self, literal: Literal) -> ScalarType:
        if literal.literal_type == "SHORT_LITERAL":
            return ScalarType(name="short", line=literal.line)

        if literal.literal_type == "INT_LITERAL":
            return ScalarType(name="int", line=literal.line)

        return ScalarType(name="bool", line=literal.line)

    #Поиск корневой переменной в цепочке индексирования массива
    def _root_variable(self, expression: Variable | ArrayAccess) -> Variable:
        current = expression

        while isinstance(current, ArrayAccess):
            current = current.array

        if not isinstance(current, Variable):
            raise SemanticError(
                "Левая часть присваивания не содержит переменную.",
                expression.line,
            )

        return current

    def _require_scalar(
        self,
        data_type: TypeNode | None,
        line: int | None,
        context: str,
    ) -> None:
        if data_type is None:
            return

        if not is_scalar(data_type):
            raise TypeMismatchError(
                f"{context}: ожидался скалярный тип, получен {type_name(data_type)}.",
                line,
            )

    def _require_compatible(
        self,
        expected: TypeNode | None,
        actual: TypeNode | None,
        line: int | None,
        context: str,
    ) -> None:
        if not types_compatible(expected, actual):
            raise TypeMismatchError(
                f"{context}: тип {type_name(actual)} нельзя использовать как {type_name(expected)}.",
                line,
            )

    def _ensure_valid_type(#Проверка, что указанный AST-тип поддерживается языком
        self,
        data_type: TypeNode,
        line: int | None,
    ) -> None:
        if not validate_type(data_type):
            raise TypeMismatchError(
                f"Неизвестный тип {type_name(data_type)}.",
                line,
            )
#вычислние значений, которые известны заранее
    def _static_integer(self, expression: Expression) -> int | None:
        if isinstance(expression, Literal):
            if expression.literal_type in {"INT_LITERAL", "SHORT_LITERAL"}:
                return int(expression.value)

            if expression.literal_type == "TRUE":
                return 1
            if expression.literal_type == "FALSE":
                return -1
            if expression.literal_type == "UNDEFINED":
                return 0

            return None

        if isinstance(expression, BinaryOperation):
            left = self._static_integer(expression.left)
            right = self._static_integer(expression.right)

            if left is None or right is None:
                return None

            if expression.operator == "add":
                return left + right
            if expression.operator == "sub":
                return left - right

        return None
