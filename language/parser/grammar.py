from language.lexer.tokens import tokens
from language.parser.parser_errors import ParserError
from language.ast.types import ScalarType, VectorType

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

from language.ast.declarations import (
    VariableDeclaration,
    VariableDeclarator,
    VectorDeclarator,
)

from language.ast.statements import (
    Block,
    DoWhileStatement,
    ExpressionStatement,
    IfStatement,
)

from language.ast.functions import (
    FunctionDefinition,
    Parameter,
    Program,
)

from language.ast.robot_commands import (
    LmsExpression,
    RobotMove,
)

#в тройных кавычках аналоги классической записи грамматики - BNF
#p[0] - левая часть продукции, p[1],p[2] и т.д. - правая часть

def p_program(p):
    """
    program : function_list
    """
    p[0] = Program(functions=p[1])


def p_function_list(p):
    """
    function_list : function_list function
                  | function
    """
    if len(p) == 3:#далее новые функции добавляются в уже сущ. список
        p[0] = p[1] + [p[2]]
    else:#первая функция создает список
        p[0] = [p[1]]


def p_function(p):
    """
    function : FUNCTION IDENTIFIER LPAREN parameter_list_opt RPAREN block RETURN expression SEMICOLON
    """
    p[0] = FunctionDefinition(
        name=p[2],
        parameters=p[4],
        body=p[6],
        return_expression=p[8],
        line=p.lineno(1),
    )


def p_parameter_list_opt(p):#function func(int c) или function work()
    """
    parameter_list_opt : parameter_list
                       | empty
    """
    if p[1] is None:
        p[0] = []
    else:
        p[0] = p[1]


def p_parameter_list(p):
    """
    parameter_list : parameter_list COMMA parameter
                   | parameter
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_parameter(p):
    """
    parameter : type IDENTIFIER
    """
    p[0] = Parameter(
        data_type=p[1],
        name=p[2],
        line=p.lineno(2),
    )


def p_type(p):
    """
    type : scalar_type
         | vector_type
    """
    p[0] = p[1]


def p_scalar_type(p):
    """
    scalar_type : BOOL
                | numeric_type
    """
    if p.slice[1].type == "BOOL":
        p[0] = ScalarType(name="bool", line=p.lineno(1))
    else:
        p[0] = p[1]


def p_numeric_type(p):
    """
    numeric_type : SHORT
                 | SHORT INT
                 | INT
    """
    if p.slice[1].type == "SHORT":
        p[0] = ScalarType(name="short", line=p.lineno(1))
    else:
        p[0] = ScalarType(name="int", line=p.lineno(1))


def p_block(p):
    """
    block : BEGIN statement_list END
    """
    p[0] = Block(
        statements=p[2],
        line=p.lineno(1),
    )


def p_statement_list(p):
    """
    statement_list : statement_list statement
                   | empty
    """
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_statement_declaration(p):
    """
    statement : declaration SEMICOLON
              | if_statement
              | loop_statement
    """
    p[0] = p[1]


def p_statement_expression(p):
    """
    statement : assignment SEMICOLON
              | function_call SEMICOLON
              | robot_command SEMICOLON
    """
    p[0] = ExpressionStatement(
        expression=p[1],
        line=p[1].line,
    )


def p_declaration(p):
    """
    declaration : variable_declaration
                | CONST variable_declaration
    """
    if len(p) == 2:
        p[0] = p[1]
        p[0].is_const = False
    else:
        p[0] = p[2]
        p[0].is_const = True
        p[0].line = p.lineno(1)


def p_variable_declaration(p):
    """
    variable_declaration : bool_declaration
                         | numeric_declaration
                         | vector_declaration
    """
    p[0] = p[1]


def p_bool_declaration(p):
    """
    bool_declaration : BOOL bool_declarator_list
    """
    p[0] = VariableDeclaration(
        data_type=ScalarType(name="bool", line=p.lineno(1)),
        variables=p[2],
        line=p.lineno(1),
    )


def p_bool_declarator_list(p):
    """
    bool_declarator_list : bool_declarator_list COMMA bool_declarator
                         | bool_declarator
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


#<имя переменной1> [set логическое выражение]
def p_bool_declarator(p):
    """
    bool_declarator : IDENTIFIER
                    | IDENTIFIER SET expression
    """
    if len(p) == 2:
        p[0] = VariableDeclarator(
            name=p[1],
            initializer=None,
            line=p.lineno(1),
        )
    else:
        p[0] = VariableDeclarator(
            name=p[1],
            initializer=p[3],
            line=p.lineno(1),
        )


def p_numeric_declaration(p):
    """
    numeric_declaration : numeric_type numeric_declarator_list
    """
    p[0] = VariableDeclaration(
        data_type=p[1],
        variables=p[2],
        line=p[1].line,
    )


def p_numeric_declarator_list(p):
    """
    numeric_declarator_list : numeric_declarator_list COMMA numeric_declarator
                            | numeric_declarator
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_numeric_declarator(p):
    """
    numeric_declarator : IDENTIFIER
                       | IDENTIFIER SET expression
    """
    if len(p) == 2:
        p[0] = VariableDeclarator(
            name=p[1],
            initializer=None,
            line=p.lineno(1),
        )
    else:
        p[0] = VariableDeclarator(
            name=p[1],
            initializer=p[3],
            line=p.lineno(1),
        )


def p_assignment(p):#expression порождает assignment -> SET правоассоциативен
    """
    assignment : lvalue SET expression
    """
    p[0] = Assignment(
        target=p[1],
        value=p[3],
        line=p[1].line,
    )


def p_lvalue_identifier(p):
    """
    lvalue : IDENTIFIER
    """
    p[0] = Variable(
        name=p[1],
        line=p.lineno(1),
    )


def p_lvalue_array(p):
    """
    lvalue : array_access
    """
    p[0] = p[1]


def p_expression(p):
    """
    expression : assignment
               | binary_expression
    """
    p[0] = p[1]


def p_binary_expression_single(p):
    """
    binary_expression : primary_expression
    """
    p[0] = p[1]


def p_binary_expression_operation(p):
    """
    binary_expression : binary_expression binary_operator primary_expression
    """
    p[0] = BinaryOperation(
        operator=p[2],
        left=p[1],
        right=p[3],
        line=p[1].line,
    )


def p_binary_operator_simple(p):
    """
    binary_operator : ADD
                    | SUB
                    | AND
                    | OR
                    | comparison_operator
    """
    p[0] = p[1]


def p_binary_operator_not(p):
    """
    binary_operator : NOT AND
                    | NOT OR
    """
    p[0] = f"not_{p[2]}"


def p_comparison_operator(p):
    """
    comparison_operator : FIRST SMALLER
                        | FIRST LARGER
                        | SECOND SMALLER
                        | SECOND LARGER
    """
    p[0] = f"{p[1]}_{p[2]}"


def p_primary_expression_literal(p):
    """
    primary_expression : literal
    """
    p[0] = p[1]


def p_primary_expression_identifier(p):
    """
    primary_expression : IDENTIFIER
    """
    p[0] = Variable(
        name=p[1],
        line=p.lineno(1),
    )


def p_primary_expression_parentheses(p):
    """
    primary_expression : LPAREN expression RPAREN
    """
    p[0] = p[2]


def p_primary_expression_special(p):
    """
    primary_expression : sizeof_expression
                       | array_access
                       | function_call
                       | lms_expression
                       | robot_move
    """
    p[0] = p[1]


def p_literal(p):
    """
    literal : INT_LITERAL
            | SHORT_LITERAL
            | TRUE
            | FALSE
            | UNDEFINED
    """
    token_type = p.slice[1].type
    p[0] = Literal(
        literal_type=token_type,
        value=p[1],
        line=p.lineno(1),
    )


def p_sizeof_type(p):
    """
    sizeof_expression : SIZEOF LPAREN scalar_type RPAREN
    """
    p[0] = Sizeof(
        target_kind="type",
        target=p[3],
        line=p.lineno(1),
    )


def p_sizeof_variable(p):
    """
    sizeof_expression : SIZEOF LPAREN IDENTIFIER RPAREN
    """
    p[0] = Sizeof(
        target_kind="variable",
        target=p[3],
        line=p.lineno(1),
    )


def p_array_access_first(p):#arr[i]
    """
    array_access : IDENTIFIER LBRACKET expression RBRACKET
    """
    variable = Variable(
        name=p[1],
        line=p.lineno(1),
    )
    p[0] = ArrayAccess(
        array=variable,
        index=p[3],
        line=p.lineno(1),
    )


def p_array_access_nested(p):#Matrix[i][j]
    """
    array_access : array_access LBRACKET expression RBRACKET
    """
    p[0] = ArrayAccess(
        array=p[1],
        index=p[3],
        line=p[1].line,
    )


def p_function_call(p):
    """
    function_call : IDENTIFIER LPAREN argument_list_opt RPAREN
    """
    p[0] = FunctionCall(
        name=p[1],
        arguments=p[3],
        line=p.lineno(1),
    )


def p_argument_list_opt(p):
    """
    argument_list_opt : argument_list
                      | empty
    """
    if p[1] is None:
        p[0] = []
    else:
        p[0] = p[1]


def p_argument_list(p):
    """
    argument_list : argument_list IDENTIFIER
                  | IDENTIFIER
    """
    if len(p) == 3:
        p[0] = p[1] + [Variable(name=p[2], line=p.lineno(2))]
    else:
        p[0] = [Variable(name=p[1], line=p.lineno(1))]


def p_lms_expression(p):
    """
    lms_expression : LMS
    """
    p[0] = LmsExpression(line=p.lineno(1))


def p_vector_type(p):
    """
    vector_type : VECTOR OF type
    """
    p[0] = VectorType(
        element_type=p[3],
        line=p.lineno(1),
    )


def p_vector_declaration(p):
    """
    vector_declaration : vector_type vector_declarator_list
    """
    p[0] = VariableDeclaration(
        data_type=p[1],
        variables=p[2],
        line=p[1].line,
    )


def p_vector_declarator_list(p):
    """
    vector_declarator_list : vector_declarator_list COMMA vector_declarator
                           | vector_declarator
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_vector_declarator(p):
    """
    vector_declarator : IDENTIFIER vector_size
                      | IDENTIFIER SET vector_initializer
                      | IDENTIFIER vector_size SET vector_initializer
    """
    if len(p) == 3:
        # Указан только размер массива.
        p[0] = VectorDeclarator(
            name=p[1],
            size=p[2],
            initializer=None,
            line=p.lineno(1),
        )
    elif len(p) == 4:
        # Размер не указан, но задан список значений.
        p[0] = VectorDeclarator(
            name=p[1],
            size=None,
            initializer=p[3],
            line=p.lineno(1),
        )
    else:
        # Указаны и размер, и список значений.
        p[0] = VectorDeclarator(
            name=p[1],
            size=p[2],
            initializer=p[4],
            line=p.lineno(1),
        )


def p_vector_size(p):
    """
    vector_size : LBRACKET expression RBRACKET
    """
    p[0] = p[2]


def p_vector_initializer(p):
    """
    vector_initializer : LBRACE initializer_list_opt RBRACE
    """
    p[0] = VectorInitializer(
        values=p[2],
        line=p.lineno(1),
    )


def p_initializer_list_opt(p):
    """
    initializer_list_opt : initializer_list
                         | empty
    """
    if p[1] is None:
        p[0] = []
    else:
        p[0] = p[1]


def p_initializer_list(p):
    """
    initializer_list : initializer_list COMMA initializer_value
                     | initializer_value
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_initializer_value(p):#обеспечивается вложенность
    """
    initializer_value : expression
                      | vector_initializer
    """
    p[0] = p[1]


def p_robot_move(p):
    """
    robot_move : RIGHT
               | LEFT
               | MOVE
               | MOVE RIGHT
               | MOVE LEFT
    """
    if len(p) == 2:
        token_type = p.slice[1].type

        if token_type == "RIGHT":
            direction = "right"
        elif token_type == "LEFT":
            direction = "left"
        else:
            direction = "vertical"
    else:
        direction = p[2]

    p[0] = RobotMove(
        direction=direction,
        line=p.lineno(1),
    )


def p_robot_command(p):
    """
    robot_command : robot_move
                  | lms_expression
    """
    p[0] = p[1]


def p_if_statement(p):
    """
    if_statement : IF expression THEN statement_or_block ELSE statement_or_block
    """
    p[0] = IfStatement(
        condition=p[2],
        then_branch=p[4],
        else_branch=p[6],
        line=p.lineno(1),
    )


def p_statement_or_block(p):
    """
    statement_or_block : statement
                       | block
    """
    p[0] = p[1]


def p_loop_statement(p):
    """
    loop_statement : DO statement_or_block WHILE expression SEMICOLON
    """
    p[0] = DoWhileStatement(
        body=p[2],
        condition=p[4],
        line=p.lineno(1),
    )


def p_empty(p):#epsilon-продукция
    """
    empty :
    """
    p[0] = None


def p_error(p):
    if p is None:
        raise ParserError(
            "Неожиданный конец программы."
        )

    raise ParserError(
        f"Неожиданный элемент {p.value!r}.",
        p.lineno,
    )