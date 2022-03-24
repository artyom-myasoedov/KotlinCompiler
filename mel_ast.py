from abc import ABC, abstractmethod
from typing import Callable, Tuple, Optional, Union, List, cast
from enum import Enum


class AstNode(ABC):
    def __init__(self, row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__()
        self.row = row
        self.line = line
        for k, v in props.items():
            setattr(self, k, v)

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return ()

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    def tree(self) -> [str, ...]:
        res = [str(self)]
        childs_temp = self.childs
        for i, child in enumerate(childs_temp):
            ch0, ch = '├', '│'
            if i == len(childs_temp) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return res

    def visit(self, func: Callable[['AstNode'], None]) -> None:
        func(self)
        map(func, self.childs)

    def __getitem__(self, index):
        return self.childs[index] if index < len(self.childs) else None


class ExprNode(AstNode):
    pass


class LiteralNode(ExprNode):
    def __init__(self, literal: str,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.literal = literal

    def __str__(self) -> str:
        return self.literal


class IdentNode(ExprNode):
    def __init__(self, name: str,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.name = str(name)

    def __str__(self) -> str:
        return str(self.name)


class BinOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    GE = '>='
    LE = '<='
    NEQUALS = '<>'
    EQUALS = '=='
    GT = '>'
    LT = '<'
    LOGICAL_AND = '&&'
    LOGICAL_OR = '||'


class Bools(Enum):
    TRUE = 'true'
    FALSE = 'false'


class Types(Enum):
    DOUBLE = 'Double'
    INTEGER = 'Int'
    STRING = 'String'
    BOOL = 'Bool'


class BinOpNode(ExprNode):
    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2

    def __str__(self) -> str:
        return str(self.op.value)


class StmtNode(ExprNode):
    pass


class TypeNode(StmtNode):
    def __init__(self, name: str, innerType: Optional[StmtNode],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.name = name
        self.innerType = innerType

    @property
    def childs(self) -> Tuple:
        return ()

    def __str__(self) -> str:
        return self.getStrView()

    def getInnerTypes(self, level: int) -> Tuple[int, str]:
        if self.innerType is not None:
            node: TypeNode = cast(TypeNode, self.innerType)
            return node.getInnerTypes(level + 1)
        return level, self.name

    def getStrView(self) -> str:
        deep, typeName = self.getInnerTypes(0)
        begin = ''
        end = ''
        if deep == 1:
            return self.name
        for i in range(deep):
            begin += 'Array<'
            end += '>'
        return begin + typeName + end


class VarDeclNode(StmtNode):
    def __init__(self, vars_type: StmtNode, *vars_list: Tuple[AstNode, ...],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.vars_type = vars_type
        self.vars_list = vars_list

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        # return self.vars_type, (*self.vars_list)
        return (self.vars_type,) + self.vars_list

    def __str__(self) -> str:
        return 'var'


class CallNode(StmtNode):
    def __init__(self, func: IdentNode, *params: Tuple[ExprNode],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.func = func
        self.params = params

    @property
    def childs(self) -> Tuple[IdentNode, ...]:
        # return self.func, (*self.params)
        return (self.func,) + self.params

    def __str__(self) -> str:
        return 'call'


class AssignNode(StmtNode):
    def __init__(self, var: IdentNode, val: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.var = var
        self.val = val

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.var, self.val

    def __str__(self) -> str:
        return '='


class SingleIfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: Optional[StmtNode] = None,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return (self.cond, self.then_stmt) + (self.else_stmt,) if self.else_stmt else ()

    def __str__(self) -> str:
        return 'if'


class MultiIfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: StmtNode = None,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return self.cond, self.then_stmt, self.else_stmt

    def __str__(self) -> str:
        return 'if'


class ForNode(StmtNode):
    def __init__(self, init: Union[StmtNode, None], cond: Union[ExprNode, StmtNode, None],
                 step: Union[StmtNode, None], body: Union[StmtNode, None] = None,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.init = init if init else _empty
        self.cond = cond if cond else _empty
        self.step = step if step else _empty
        self.body = body if body else _empty

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.init, self.cond, self.step, self.body

    def __str__(self) -> str:
        return 'for'


class StmtListNode(StmtNode):
    def __init__(self, *exprs: StmtNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.exprs = exprs

    @property
    def childs(self) -> Tuple[StmtNode, ...]:
        return self.exprs

    def __str__(self) -> str:
        return '...'


class WhenInnerNode(StmtNode):
    def __init__(self, expr: ExprNode, stmt: StmtNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.expr = expr
        self.stmt = stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode]:
        return self.expr, self.stmt

    def __str__(self) -> str:
        return '->'


class WhenNode(StmtNode):
    def __init__(self, ident: IdentNode, finalBlock: StmtListNode, *optionallocks: WhenInnerNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.ident = ident
        self.optionallocks = optionallocks
        self.finalBlock = finalBlock

    @property
    def childs(self) -> Tuple[StmtNode, ...]:
        return (self.ident, self.finalBlock) + self.optionallocks

    def __str__(self) -> str:
        return 'when'


class VarTypeNode(StmtNode):
    def __init__(self, var: IdentNode, _type: IdentNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.var = var
        self.type = _type

    @property
    def childs(self) -> Tuple:
        return ()

    def __str__(self) -> str:
        return self.var.name + ':' + str(self.type)


class VarInitNode(StmtNode):
    def __init__(self, varType: VarTypeNode, val: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.varType = varType
        self.val = val

    @property
    def childs(self) -> Tuple[VarTypeNode, ExprNode]:
        return self.varType, self.val

    def __str__(self) -> str:
        return 'var'


class WhileNode(StmtNode):
    def __init__(self, cond: ExprNode, body: StmtListNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.cond = cond
        self.body = body

    @property
    def childs(self) -> Tuple[ExprNode, StmtListNode]:
        return self.cond, self.body

    def __str__(self) -> str:
        return 'while'


class CommonFunDeclrNode(StmtNode):
    def __init__(self, name: IdentNode, retType: TypeNode, body: StmtListNode, *params: Tuple[VarTypeNode, ...],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.params = params
        self.name = name
        self.retType = retType
        self.body = body

    @property
    def childs(self) -> Tuple[StmtListNode]:
        return self.body,

    def __str__(self) -> str:
        return 'fun ' + self.name.name + '(' + self.strParams() + ')' + self.strRetVal()

    def strParams(self) -> str:
        s: str = ''
        for i in self.params:
            s += i.__str__()
            s += ', '
        return s[:-2] if s != '' else ''

    def strRetVal(self) -> str:
        return ': ' + str(self.retType)


class SimpleFunDeclrNode(StmtNode):
    def __init__(self, name: IdentNode, retType: TypeNode, expr: ExprNode, *params: Tuple[VarTypeNode, ...],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.params = params
        self.name = name
        self.retType = retType
        self.expr = expr

    @property
    def childs(self) -> Tuple[ExprNode]:
        return self.expr,

    def __str__(self) -> str:
        return 'fun ' + self.name.name + '(' + self.strParams() + ')' + self.strRetVal()

    def strParams(self) -> str:
        s: str = ''
        for i in self.params:
            s += i.__str__()
            s += ', '
        return s[:-2] if s != '' else ''

    def strRetVal(self) -> str:
        return ': ' + str(self.retType)


class ForArrNode(StmtNode):
    def __init__(self, param: IdentNode, arr: IdentNode, body: StmtListNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.param = param
        self.body = body
        self.arr = arr

    @property
    def childs(self) -> Tuple[IdentNode, IdentNode, StmtListNode]:
        return self.param, self.arr, self.body

    def __str__(self) -> str:
        return 'for ' + self.param.name + ' in ' + self.arr.name


class ForRangeNode(StmtNode):
    def __init__(self, param: IdentNode, start: ExprNode, end: ExprNode, body: StmtListNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.param = param
        self.body = body
        self.start = start
        self.end = end

    @property
    def childs(self) -> Tuple[IdentNode, StmtListNode]:
        return self.param, self.body

    def __str__(self) -> str:
        return 'for ' + self.param.name + ' in ' + self.start.__str__() + '..' + self.end.__str__()


class EmptyArrNode(StmtNode):
    def __init__(self, size: int,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.size = size

    @property
    def childs(self) -> Tuple:
        return ()

    def __str__(self) -> str:
        return 'Array(' + str(self.size) + ')'


class ArrOfNode(StmtNode):
    def __init__(self, *params: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.params = params

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return self.params

    def __str__(self) -> str:
        return 'arrayOf'


_empty = StmtListNode()
