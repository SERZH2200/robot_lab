class ParserError(Exception):
    def __init__(
        self,
        message: str,
        line: int | None = None,
    ):
        self.message = message
        self.line = line

        if line is None:
            text = message
        else:
            text = f"{message} (строка {line})"

        super().__init__(text)