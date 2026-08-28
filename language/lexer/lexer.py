import ply.lex as lex

from language.lexer.tokens import tokens, reserved
from language.lexer.lex_err import LexerError

t_LPAREN = r"\("
t_RPAREN = r"\)"

t_LBRACKET = r"\["
t_RBRACKET = r"\]"

t_LBRACE = r"\{"
t_RBRACE = r"\}"

t_COMMA = r","
t_SEMICOLON = r";"

t_ignore = " \t\r"

def t_SHORT_LITERAL(t):
    r"[sS][+-]?\d+"

    # S123  -> 123
    # S-123 -> -123

    t.value = int(t.value[1:])

    return t


def t_INT_LITERAL(t):
    r"[+-]?\d+"

    t.value = int(t.value)

    return t


def t_IDENTIFIER(t):
    r"[A-Za-z_][A-Za-z0-9_]*"

    normalized = t.value.lower()
    token_type = reserved.get(normalized)

    if token_type is not None:
        t.type = token_type
        t.value = normalized
    else:
        # Имена переменных и функций тоже регистронезависимы.
        t.value = normalized

    return t

def t_newline(t):
    r"\n+"

    t.lexer.lineno += len(t.value)

def _find_column(text: str, lexpos: int) -> int:
    line_start = text.rfind("\n", 0, lexpos)#последнее вхождение "\n" перед lexpos

    if line_start < 0:#перед ошибкой вообще нет \n, тогда мы с -1 все равно получим верный столбец
        line_start = -1

    return lexpos - line_start


def t_error(t):
    column = _find_column(
        t.lexer.lexdata,
        t.lexpos,
    )

    character = t.value[0]

    raise LexerError(message=f"Недопустимый символ {character!r}",line=t.lexer.lineno,
        column=column,
    )

def build_lexer():
    return lex.lex()