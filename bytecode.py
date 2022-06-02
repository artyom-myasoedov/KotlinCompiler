from enum import Enum
from typing import List, Union
from mel_ast import BaseType


class ByteCodeOperation(Enum):
    LOAD_LOCAL_OR_ARG = 'load_local_or_arg'

    def __str__(self):
        return self.value


TYPE_TO_COMMAND_MAP = {
    BaseType.STR: {
        ByteCodeOperation.LOAD_LOCAL_OR_ARG: 'astore'
    },
    BaseType.INT: {
        ByteCodeOperation.LOAD_LOCAL_OR_ARG: 'istore'

    },
    BaseType.FLOAT: {
        ByteCodeOperation.LOAD_LOCAL_OR_ARG: 'fstore'
    },
    BaseType.BOOL: {
        ByteCodeOperation.LOAD_LOCAL_OR_ARG: 'istore'
    }

}


class CodeLabel:
    def __init__(self):
        self.index = None

    def __str__(self):
        return 'IL_' + str(self.index)


class CodeLine:
    def __init__(self, code: str, *params: Union[str, int, CodeLabel], label: CodeLabel = None):
        self.code = code
        self.label = label
        self.params = params

    def __str__(self):
        line = ''
        if self.label:
            line += str(self.label) + ': '
        line += self.code
        for p in self.params:
            line += ' ' + str(p)
        return line


class CodeGenerator:
    def __init__(self):
        self.code_lines: List[CodeLine] = []

    def add(self, code: str, *params: Union[str, int, CodeLabel], label: CodeLabel = None):
        self.code_lines.append(CodeLine(code, *params, label=label))

    @property
    def code(self) -> [str, ...]:
        index = 0
        for cl in self.code_lines:
            line = cl.code
            if cl.label:
                cl.label.index = index
                index += 1
        code: List[str] = []
        for cl in self.code_lines:
            code.append(str(cl))
        return code

    def start(self) -> None:
        self.add('.source                  Main.java')
        self.add('.class                   public Main')
        self.add('.super                   java/lang/Object')
        self.add('')

    def end(self) -> None:
        self.add('}')

    def prepare_built_in(self):
        self.add()

    def main(self) -> None:
        self.add()
