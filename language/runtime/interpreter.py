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
from language.ast.types import VectorType
from language.runtime.arithmetic import (
    INT_MAX,
    INT_MIN,
    SHORT_MAX,
    SHORT_MIN,
    add,
    sub,
)
from language.runtime.arrays import (
    convert_value,
    get_element,
    get_index,
    make_sized_vector,
    set_element,
    type_size,
    value_size,
)
from language.runtime.call_stack import CallStack
from language.runtime.environment import Environment
from language.runtime.frame import Frame
from language.runtime.functions import FunctionRegistry
from language.runtime.logic import compare, logical_and, logical_not, logical_or
from language.runtime.robot import RobotController
from language.runtime.runtime_errors import (
    RobotRuntimeError,
    RuntimeConstError,
    RuntimeFunctionError,
    RuntimeLanguageError,
    RuntimeOverflowError,
    RuntimeTypeError,
    RuntimeExecutionLimitError,
    RuntimeCallStackOverflowError,
    RuntimeVectorError,
)
from language.runtime.values import (
    BoolState,
    BoolValue,
    IntValue,
    RuntimeValue,
    ShortValue,
    VectorValue,
    clone_value,
    default_value,
    to_bool,
)


class Interpreter:
    def __init__(
        self,
        program: Program,
        robot: RobotController | None = None,
        max_steps: int = 100_000,
        max_call_depth: int = 200,
    ):
        self.program = program
        self.robot = robot
        self.functions = FunctionRegistry(program)
        self.call_stack = CallStack()

        self.max_steps = max_steps
        self.steps = 0
        self.max_call_depth = max_call_depth


    def _tick(self, line: int | None = None) -> None:#счётчик шагов интерпретатора
        self.steps += 1

        if self.steps > self.max_steps:
            raise RuntimeExecutionLimitError(
                self.max_steps,
                line,
            )

    def run(self) -> RuntimeValue:
        self.steps = 0
        return self._call_function("work", [])

    def _current_environment(self) -> Environment:
        return self.call_stack.current().environment#окружение текущей функции

    def _call_function(self, name: str, arguments: list[RuntimeValue], line: int | None = None, ) -> RuntimeValue:
        if len(self.call_stack) >= self.max_call_depth:
            raise RuntimeCallStackOverflowError(
                self.max_call_depth,
                line,
            )
        function = self.functions.resolve(name, line)

        if len(arguments) != len(function.parameters):
            raise RuntimeFunctionError(
                f"Функция '{function.name}' ожидает {len(function.parameters)} аргумент(а/ов), "
                f"получено {len(arguments)}.",
                line,
            )

        environment = Environment(function.name)

        for parameter, argument in zip(function.parameters, arguments):
            #clone_value для того, чтобы изменение параметра внутри функции не влияло на переменную вызывающей
            converted = convert_value(clone_value(argument), parameter.data_type, parameter.line)
            environment.declare(
                parameter.name,
                parameter.data_type,
                converted,
                is_const=False,
                line=parameter.line,
            )

        frame = Frame(function.name, environment)
        self.call_stack.push(frame)

        try:
            self._execute_block(function.body)
            result = self._evaluate(function.return_expression)
            return clone_value(result)
        finally:#даже если будет ошибка кажр будет снят со стека
            self.call_stack.pop()

    def _execute_block(self, block: Block) -> None:
        for statement in block.statements:
            self._execute_statement(statement)

    def _execute_statement(self, statement: Statement) -> None:
        self._tick(statement.line)

        if isinstance(statement, VariableDeclaration):
            self._execute_declaration(statement)
            return

        if isinstance(statement, ExpressionStatement):
            self._evaluate(statement.expression)
            return

        if isinstance(statement, IfStatement):
            condition = to_bool(self._evaluate(statement.condition)).value

            if condition == BoolState.TRUE:
                self._execute_statement(statement.then_branch)
            elif condition == BoolState.FALSE:
                self._execute_statement(statement.else_branch)

            return

        if isinstance(statement, DoWhileStatement):
            while True:
                self._tick(statement.line)

                self._execute_statement(statement.body)
                condition = to_bool(self._evaluate(statement.condition)).value

                if condition != BoolState.TRUE:
                    break

            return

        if isinstance(statement, Block):
            self._execute_block(statement)
            return

        raise RuntimeLanguageError(
            f"Неизвестный тип предложения {type(statement).__name__}.",
            statement.line,
        )

    def _execute_declaration(self, declaration: VariableDeclaration) -> None:
        environment = self._current_environment()

        for declarator in declaration.variables:
            if isinstance(declarator, VariableDeclarator):
                if declarator.initializer is None:
                    value = default_value(declaration.data_type)
                else:
                    value = self._evaluate(declarator.initializer)
                    value = convert_value(
                        value,
                        declaration.data_type,
                        declarator.line,
                    )

                environment.declare(
                    declarator.name,
                    declaration.data_type,
                    value,
                    declaration.is_const,
                    declarator.line,
                )
                continue

            if isinstance(declarator, VectorDeclarator):
                self._execute_vector_declaration(
                    declaration,
                    declarator,
                    environment,
                )
                continue

            raise RuntimeLanguageError(
                f"Неизвестный тип объявления {type(declarator).__name__}.",
                declarator.line,
            )

#Создание vector по размеру или инициализатору и проверяет их согласованность.
    def _execute_vector_declaration(
        self,
        declaration: VariableDeclaration,
        declarator: VectorDeclarator,
        environment: Environment,
    ) -> None:
        if not isinstance(declaration.data_type, VectorType):
            raise RuntimeVectorError(
                f"'{declarator.name}' объявлен как массив без типа vector.",
                declarator.line,
            )

        size = None

        if declarator.size is not None:
            size = get_index(
                self._evaluate(declarator.size),
                declarator.size.line,
            )

            if size < 0:
                raise RuntimeVectorError(
                    "Размер vector не может быть отрицательным.",
                    declarator.size.line,
                )

        if declarator.initializer is not None:
            value = self._evaluate_vector_initializer(
                declarator.initializer,
                declaration.data_type,
            )

            if size is not None and len(value.elements) != size:
                raise RuntimeVectorError(
                    f"Размер vector '{declarator.name}' равен {size}, "
                    f"но инициализатор содержит {len(value.elements)} элемент(а/ов).",
                    declarator.line,
                )
        else:
            if size is None:
                raise RuntimeVectorError(
                    f"Для vector '{declarator.name}' не указан ни размер, ни инициализатор.",
                    declarator.line,
                )

            value = make_sized_vector(
                declaration.data_type.element_type,
                size,
                declarator.line,
            )

        environment.declare(
            declarator.name,
            declaration.data_type,
            value,
            declaration.is_const,
            declarator.line,
        )

    def _evaluate_vector_initializer(#рекурсивное построение многомерного массива, если требуется, иначе - просто создается вектор
        self,
        initializer: VectorInitializer,
        vector_type: VectorType,
    ) -> VectorValue:
        values: list[RuntimeValue] = []
        element_type = vector_type.element_type

        for item in initializer.values:
            if isinstance(item, VectorInitializer):
                if not isinstance(element_type, VectorType):
                    raise RuntimeVectorError(
                        "Вложенный инициализатор не соответствует типу vector.",
                        item.line,
                    )

                values.append(
                    self._evaluate_vector_initializer(item, element_type)
                )
                continue

            if isinstance(element_type, VectorType):
                raise RuntimeVectorError(
                    "Для вложенного vector ожидается вложенный инициализатор.",
                    item.line,
                )

            value = self._evaluate(item)
            values.append(convert_value(value, element_type, item.line))

        return VectorValue(values)

#вычисление выражения и возврат RuntimeValue
    def _evaluate(self, expression: Expression) -> RuntimeValue:
        self._tick(expression.line)

        if isinstance(expression, Literal):
            return self._evaluate_literal(expression)

        if isinstance(expression, Variable):
            return self._current_environment().get(
                expression.name,
                expression.line,
            )

        if isinstance(expression, BinaryOperation):
            return self._evaluate_binary_operation(expression)

        if isinstance(expression, Assignment):
            value = self._evaluate(expression.value)
            return self._assign(expression.target, value)

        if isinstance(expression, ArrayAccess):
            vector, index = self._resolve_array_parent(expression)
            return get_element(vector, index, expression.line)

        if isinstance(expression, Sizeof):
            return self._evaluate_sizeof(expression)

        if isinstance(expression, FunctionCall):
            arguments = [
                clone_value(
                    self._current_environment().get(argument.name, argument.line)
                )
                for argument in expression.arguments
            ]
            return self._call_function(
                expression.name,
                arguments,
                expression.line,
            )

        if isinstance(expression, RobotMove):
            return self._execute_robot_move(expression)

        if isinstance(expression, LmsExpression):
            return self._execute_lms(expression)

        raise RuntimeLanguageError(
            f"Неизвестный тип выражения {type(expression).__name__}.",
            expression.line,
        )

    def _evaluate_literal(self, literal: Literal) -> RuntimeValue:
        if literal.literal_type == "SHORT_LITERAL":
            value = int(literal.value)

            if value < SHORT_MIN or value > SHORT_MAX:
                raise RuntimeOverflowError(
                    f"Литерал {value} не помещается в short.",
                    literal.line,
                )

            return ShortValue(value)

        if literal.literal_type == "INT_LITERAL":
            value = int(literal.value)

            if value < INT_MIN or value > INT_MAX:
                raise RuntimeOverflowError(
                    f"Литерал {value} не помещается в int.",
                    literal.line,
                )

            return IntValue(value)

        if literal.literal_type == "TRUE":
            return BoolValue(BoolState.TRUE)

        if literal.literal_type == "FALSE":
            return BoolValue(BoolState.FALSE)

        if literal.literal_type == "UNDEFINED":
            return BoolValue(BoolState.UNDEFINED)

        raise RuntimeTypeError(
            f"Неизвестный тип литерала '{literal.literal_type}'.",
            literal.line,
        )

    def _evaluate_binary_operation(
        self,
        expression: BinaryOperation,
    ) -> RuntimeValue:
        left = self._evaluate(expression.left)
        right = self._evaluate(expression.right)
        operator = expression.operator

        if operator == "add":
            return add(left, right, expression.line)

        if operator == "sub":
            return sub(left, right, expression.line)

        if operator == "and":
            return logical_and(left, right)

        if operator == "or":
            return logical_or(left, right)

        if operator == "not_and":
            return logical_not(logical_and(left, right))

        if operator == "not_or":
            return logical_not(logical_or(left, right))

        if operator in {
            "first_smaller",
            "first_larger",
            "second_smaller",
            "second_larger",
        }:
            return compare(operator, left, right)

        raise RuntimeLanguageError(
            f"Неизвестный бинарный оператор '{operator}'.",
            expression.line,
        )

    def _assign(
        self,
        target: Variable | ArrayAccess,
        value: RuntimeValue,
    ) -> RuntimeValue:
        environment = self._current_environment()

        if isinstance(target, Variable):
            variable = environment.resolve(target.name, target.line)
            converted = convert_value(value, variable.data_type, target.line)
            return environment.assign(target.name, converted, target.line)

        if isinstance(target, ArrayAccess):
            root = self._root_variable(target)
            variable = environment.resolve(root.name, root.line)

            if variable.is_const:
                raise RuntimeConstError(
                    f"Нельзя изменить элемент константы '{variable.name}'.",
                    target.line,
                )

            element_type = self._array_element_type(variable.data_type, target)
            converted = convert_value(value, element_type, target.line)
            vector, index = self._resolve_array_parent(target)
            return set_element(vector, index, converted, target.line)

        raise RuntimeLanguageError(
            "Некорректная левая часть присваивания.",
            target.line,
        )

    #Находит непосредственно индексируемый VectorValue и вычисляет индекс
    def _resolve_array_parent(
        self,
        access: ArrayAccess,
    ) -> tuple[VectorValue, int]:
        if isinstance(access.array, Variable):
            value = self._current_environment().get(
                access.array.name,
                access.array.line,
            )
        else:
            value = self._evaluate(access.array)

        if not isinstance(value, VectorValue):
            raise RuntimeVectorError(
                "Попытка индексировать значение, которое не является vector.",
                access.line,
            )

        index = get_index(self._evaluate(access.index), access.index.line)
        return value, index

    def _array_element_type(#какой тип имеет элемень после всех индексов
        self,
        data_type: TypeNode,
        access: ArrayAccess,
    ) -> TypeNode:
        indices = 1
        current = access.array

        while isinstance(current, ArrayAccess):
            indices += 1
            current = current.array

        result = data_type

        for _ in range(indices):
            if not isinstance(result, VectorType):
                raise RuntimeVectorError(
                    "Количество индексов превышает вложенность vector.",
                    access.line,
                )

            result = result.element_type

        return result

    def _root_variable(self, access: ArrayAccess) -> Variable:
        current = access.array

        while isinstance(current, ArrayAccess):
            current = current.array

        if not isinstance(current, Variable):
            raise RuntimeVectorError(
                "Не удалось определить корневой vector.",
                access.line,
            )

        return current

    def _evaluate_sizeof(self, expression: Sizeof) -> RuntimeValue:
        if expression.target_kind == "type":
            return IntValue(type_size(expression.target, expression.line))

        if expression.target_kind == "variable":
            value = self._current_environment().get(
                str(expression.target),
                expression.line,
            )
            return IntValue(value_size(value))

        raise RuntimeTypeError(
            f"Неизвестный вариант sizeof '{expression.target_kind}'.",
            expression.line,
        )

    def _execute_robot_move(self, expression: RobotMove) -> RuntimeValue:
        if self.robot is None:
            raise RobotRuntimeError(
                "Команда перемещения вызвана без подключённого робота.",
                expression.line,
            )

        if expression.direction == "left":
            result = self.robot.move_left()
        elif expression.direction == "right":
            result = self.robot.move_right()
        elif expression.direction == "vertical":
            result = self.robot.move_vertical()
        else:
            raise RobotRuntimeError(
                f"Неизвестное направление '{expression.direction}'.",
                expression.line,
            )

        if result is None or result == 0:
            return BoolValue(BoolState.UNDEFINED)

        if result not in {-1, 1}:
            raise RobotRuntimeError(
                f"Робот вернул недопустимый результат перемещения: {result}.",
                expression.line,
            )

        return ShortValue(int(result))

    def _execute_lms(self, expression: LmsExpression) -> RuntimeValue:
        if self.robot is None:
            raise RobotRuntimeError(
                "LMS вызван без подключённого робота.",
                expression.line,
            )

        return IntValue(int(self.robot.lms()))
