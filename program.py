import os

import bytecode
import mel_parser as parser
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
    print('bytecode:')
    try:
        gen = bytecode.CodeGenerator()
        gen.start()
        prog.gen_bytecode(gen, True) # gen funcs
        gen.main()
        prog.gen_bytecode(gen) # gen main body
        gen.end()
        print(*gen.code, sep=os.linesep)
    except semantic.SemanticException as e:
        print('Ошибка: {}'.format(e.message))
        return
    print()
    '''
    print('bytecode:')
    try:
        gen = msil.CodeGenerator()
        gen.start()
        prog.msil(gen)
        gen.end()
        print(*gen.code, sep=os.linesep)
    except semantic.SemanticException as e:
        print('Ошибка: {}'.format(e.message))
        return
    print()
    '''

    #todo статические методы
    #todo глобальные переменные как статические члены класса, записывать их отдельно
    # один раз пройтись собрать функции в один контейнер, глобалы в другой тело маина в третий и потом каждый нагенерить