reserved = {
    "bool": "BOOL",
    "short": "SHORT",
    "int": "INT",
    "vector": "VECTOR",
    "of": "OF",

    "true": "TRUE",
    "false": "FALSE",
    "undefined": "UNDEFINED",

    "set": "SET",

    "add": "ADD",
    "sub": "SUB",

    "first": "FIRST",
    "second": "SECOND",
    "smaller": "SMALLER",
    "larger": "LARGER",

    "and": "AND",
    "or": "OR",
    "not": "NOT",

    "if": "IF",
    "then": "THEN",
    "else": "ELSE",
    "do": "DO",
    "while": "WHILE",

    "begin": "BEGIN",
    "end": "END",

    "function": "FUNCTION",
    "return": "RETURN",

    "move": "MOVE",
    "left": "LEFT",
    "right": "RIGHT",
    "lms": "LMS",

    "sizeof": "SIZEOF",

    "const": "CONST",
}

tokens = [
    "IDENTIFIER",

    "INT_LITERAL",
    "SHORT_LITERAL",

    "LPAREN",
    "RPAREN",
    "LBRACKET",
    "RBRACKET",
    "LBRACE",
    "RBRACE",
    "COMMA",
    "SEMICOLON",
] + list(reserved.values())