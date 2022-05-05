from lark import Lark
from lark.lexer import Token
from lark.visitors import InlineTransformer

from mel_ast import *

parser = Lark('''
    %import common.NUMBER
    %import common.ESCAPED_STRING
    %import common.CNAME
    %import common.NEWLINE
    %import common.WS
    %import common.INT

    %ignore WS

    COMMENT: "/*" /(.|\\n|\\r)+/ "*/"
        |  "//" /(.)+/ NEWLINE
    %ignore COMMENT

    num: NUMBER  -> literal
    str: ESCAPED_STRING  -> literal
    ident: CNAME 
    int: INT -> literal
    bool: TRUE
        | FALSE

    keywords: "while"
    
    ADD:     "+"
    SUB:     "-"
    MUL:     "*"
    DIV:     "/"
    AND:     "&&"
    OR:      "||"
    GE:      ">="
    LE:      "<="
    NEQUALS: "!="
    EQUALS:  "=="
    GT:      ">"
    LT:      "<"
    
    TRUE:    "true"
    FALSE:   "false"
    ARRAY: "Array"

    call: ident "(" ( expr ( "," expr )* )? ")"

    ?group: num | str
        | bool
        | ident
        | array_init
        | call
        | "(" expr ")"
        | arr_call

    ?mult: group
        | mult ( MUL | DIV ) group  -> bin_op

    ?add: mult
        | add ( ADD | SUB ) mult  -> bin_op

    ?compare1: add
        | add ( GT | LT | GE | LE ) add  -> bin_op

    ?compare2: compare1
        | compare1 ( EQUALS | NEQUALS ) compare1  -> bin_op

    ?logical_and: compare2
        | logical_and AND compare2  -> bin_op

    ?logical_or: logical_and
        | logical_or OR logical_and  -> bin_op

    ?expr: logical_or
    
    ?stmt_group: "{" stmt_list "}"
    
    ?when_inner: expr "->" stmt_group

    ?when: "when" "(" ident ")" "{" when_inner ( when_inner )* "else" "->" stmt_group "}" 
    
    ?type: ident
        | array_type
    
    ?array_type: ARRAY "<" type ">"
    
    arr_call: ident "[" expr "]"
    
    array_init: "arrayOf(" ( expr ( "," expr )* )? ")" -> arr_of
        | "Array(" int ")"                             -> empty_arr
    
    var_type: ident ":" type
    
    assign: ident "=" expr
        | arr_call "=" expr

    var_decl: "val" var_type "=" expr -> var_init
        | "var" var_type "=" expr      -> var_init
        | "var" var_type               

    ?simple_stmt: assign
        | call

    ?for: "for" "(" ident "in" ident ")" stmt_group -> for_arr
        | "for" "(" ident "in" int ".." int ")" stmt_group -> for_range
        
    
    if: "if" "(" expr ")" stmt_group  ("else" stmt_group)? -> single_if
        | "if" "(" expr ")" stmt_group  "else" if -> multi_if
        
    fun_declr: "fun" ident "(" (var_type ( "," var_type )* )? ")" ":" type stmt_group -> common_fun_declr
        | "fun" ident "(" (var_type ( "," var_type )* )? ")" ":" type "=" expr -> simple_fun_declr

    return: "return" expr
    
    ?stmt: var_decl
        | "while" "(" expr ")" stmt_group -> while
        | simple_stmt
        | if
        | for
        | stmt_group
        | when
        | fun_declr
        | return

    stmt_list: ( stmt )*

    ?prog: stmt_list

    ?start: prog
''', start='start')  # , parser='lalr')


class MelASTBuilder(InlineTransformer):
    def __init__(self):
        super().__init__()
        self.arrCount = 0

    def __getattr__(self, item):
        if isinstance(item, str) and item.upper() == item:
            return lambda x: x

        if item in ('bin_op',):
            def get_bin_op_node(*args):
                op = BinOp(args[1].value)
                return BinOpNode(op, args[0], args[2],
                                 **{'token': args[1], 'line': args[1].line, 'column': args[1].column})

            return get_bin_op_node

        elif item in ('when',):
            def get_when_node(*args):
                return WhenNode(args[0], list(args[1:-1]), args[-1],
                                 **{'token': args[0], 'line': args[0].line, 'column': args[0].column})

            return get_when_node

        elif item in ('common_fun_declr',):
            def get_common_fun_declr_node(*args):
                args = [args[0], args[-2], args[-1], tuple(args[1:-2])]
                return CommonFunDeclrNode(*args,
                                          **{'token': args[0], 'line': args[0].line, 'column': args[0].column})

            return get_common_fun_declr_node

        elif item in ('simple_fun_declr',):
            def get_simple_fun_declr_node(*args):
                args = [args[0], args[-2], StmtListNode(ReturnNode(args[-1])), tuple(args[1:-2])]
                return CommonFunDeclrNode(*args,
                                          **{'token': args[0], 'line': args[0].line, 'column': args[0].column})

            return get_simple_fun_declr_node

        elif item in ('bool',):
            def get_bool(*args):
                return LiteralNode(str(Bools(args[0]).value),
                                   **{'token': args[0], 'line': args[0].line, 'column': args[0].column})

            return get_bool

        elif item in ('array_type',):
            def get_type(*args):
                return TypeNode(name=args[0], innerType=args[1], **{'token': args[0], 'line': args[0].line, 'column': args[0].column})

            return get_type

        else:
            def get_node(*args):
                props = {}
                if len(args) == 1 and isinstance(args[0], Token):
                    props['token'] = args[0]
                    props['line'] = args[0].line
                    props['column'] = args[0].column
                    args = [args[0].value]
                cls = eval(''.join(x.capitalize() for x in item.split('_')) + 'Node')
                return cls(*args, **props)

            return get_node


def parse(prog: str) -> StmtListNode:
    prog = parser.parse(str(prog))
    # print(prog.pretty('  '))
    prog = MelASTBuilder().transform(prog)
    return prog
