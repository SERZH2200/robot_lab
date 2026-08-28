class LexerError(Exception):
    def __init__(self,message: str,line: int,column: int):
        self.message = message
        self.line = line
        self.column = column

        location = f"line {line}, column {column}"

        super().__init__(f"{message} ({location})")