from language.ast.functions import FunctionDefinition, Program
from language.runtime.runtime_errors import RuntimeFunctionError

#опять-таки похоже на symbol_table, но уже работает в рантайм
class FunctionRegistry:
    def __init__(self, program: Program):
        self.functions: dict[str, FunctionDefinition] = {}

        for function in program.functions:
            name = function.name.lower()

            if name in self.functions:
                raise RuntimeFunctionError(
                    f"Функция '{function.name}' объявлена повторно.",
                    function.line,
                )

            self.functions[name] = function

    def resolve(
        self,
        name: str,
        line: int | None = None,
    ) -> FunctionDefinition:
        function = self.functions.get(name.lower())

        if function is None:
            raise RuntimeFunctionError(
                f"Неизвестная функция '{name}'.",
                line,
            )

        return function
