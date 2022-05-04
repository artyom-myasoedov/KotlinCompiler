import os
import mel_parser


def main():
    prog = '''
    
    fun myFunc(i: Int, b: String): Double {
    print()
    }
    
    fun pow(i: Int, b: String): Int = b * i
    
    val i: Int = 10
    var b: Double = 11.2
    var c: String
    c = "str"
    when(i) {
    1 -> { i = 4}
    2 -> { i = 4}
    else -> {c = i - 10}
    }
    while (i>0) {
    when(i) {
    1 -> { i = 4}
    else -> {c = i - 10}
    }
    }
    if (a == b) {
    a = c
    e = 1-4
    } else if (empty()) {
    i = call()
    } else {
    print()}
    
    for (i in 5..7) {
    a = b
    plus(a)
    }
    
    for (i in arr) {
    a = b
    c = true
    plus(a)
    var c: Array<Array<Double>> = Array(30)
    var c: Array<Array<Double>> = arrayOf(30, call(1), 4.3)
    c[a + 3] =  c[3]
    }
    '''
    prog = mel_parser.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
