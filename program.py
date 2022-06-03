import os
import mel_parser as parser
import msil
import semantic


def execute(prog: str) -> None:
    prog = parser.parse(prog)

    print('ast:')
    print(*prog.tree, sep=os.linesep)
    print()

    print('semantic_check:')
    try:
        scope = semantic.prepare_global_scope()
        prog.semantic_check(scope)
        print(*prog.tree, sep=os.linesep)
    except semantic.SemanticException as e:
        print('Ошибка: {}'.format(e.message))
        return
    print()

    print('msil:')
    try:
        gen = msil.CodeGenerator()
        gen.msil_gen_program(prog)
        print(*gen.code, sep=os.linesep)
    except msil.MsilException as e:
        print('Ошибка: {}'.format(e.message))
        return
    print()