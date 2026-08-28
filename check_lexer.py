from language.lexer.lexer import build_lexer


source = """function WORK(short Count)
begin
    vector of short values[3] set {S1, S-2, S3};
    bool result set true;

    if Count first larger S0 then
        move right;
    else
        move left;
end
"""


lexer = build_lexer()
lexer.input(source)

for token in lexer:
    print(
        token.type,
        token.value,
        f"строка={token.lineno}",
        f"позиция={token.lexpos}",
    )