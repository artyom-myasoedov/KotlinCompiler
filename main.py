import os
import mel_parser
import program


def main():
    prog = '''
    
    fun myFunc(i: Int, b: String): Int {
    println("e")
    return 1
    }
    
    fun pow(i: Int, b: Int): Float = b * i
    
    val i: Int = 10
    var b: Float = 11.2
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
    var a: Int = 2
    if (a == b) {
    a = 10
    var e: Int = 1-4
    } else if (pow(10, a) > 0) {
    var t: String = readLine()
    } else {
    println("")
    }
    
    for (aaa in 5..7) {
    a = 10*12
    myFunc(a, c)
    }
    var arr: Array<Int> = Array(10)
    for (ip in arr) {
    var co: Boolean = true
    println(1)
    var aa: Array<Array<Float>> = Array(30)
    var ar2: Array<Array<Float>> = arrayOf(arrayOf(0.1))
    aa[a + 3][2] =  ar2[3][1]
    }
    '''
    program.execute(prog)

if __name__ == "__main__":
    main()
