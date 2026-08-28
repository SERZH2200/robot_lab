class RuntimeLanguageError(Exception):
    def __init__(self, message: str, line: int | None = None):
        self.message = message
        self.line = line

        if line is None:
            text = message
        else:
            text = f"{message} (строка {line})"

        super().__init__(text)

class RuntimeCallStackOverflowError(RuntimeLanguageError):
    def __init__(self, limit: int, line: int | None = None):
        message = (
            f"Превышена максимальная глубина вызовов функций "
            f"({limit})."
        )

        super().__init__(message, line)

class RuntimeExecutionLimitError(RuntimeLanguageError):
    def __init__(self, limit: int, line: int | None = None):
        message = (
            f"Превышен допустимый лимит выполнения программы "
            f"({limit} шагов)."
        )

        super().__init__(message, line)

class RuntimeTypeError(RuntimeLanguageError):
    pass


class RuntimeOverflowError(RuntimeLanguageError):
    pass


class RuntimeVariableError(RuntimeLanguageError):
    pass


class RuntimeConstError(RuntimeLanguageError):
    pass


class RuntimeVectorError(RuntimeLanguageError):
    pass


class RuntimeFunctionError(RuntimeLanguageError):
    pass


class RobotRuntimeError(RuntimeLanguageError):
    pass
