from language.lexer.lexer import build_lexer
from language.parser.parser import build_parser


source = """
function work()
begin
    short x set S5;
    x set x add S1;
end
return x;
"""

lexer = build_lexer()
parser = build_parser()

result = parser.parse(
    source,
    lexer=lexer,
)

print(result)
print(type(result))