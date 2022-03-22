import os
import mel_parser


def main():
    prog = '''
        int g, g2 = g, g = 90;

        a = input(); b = input();  /* comment 1
        c = input();
        */
        for (int i = 0, j = 8; ((i <= 5)) && g; i = i + 1, print(5))
            for(; a < b;)
                if (a > 7 + b) {
                    c = a + b * (2 - 1) + 0;  // comment 2
                    b = "98\tура";
                }
                else if (f)
                    output(c + 1, 89.89);
        for(;;);
    '''
    prog = '''
    val i: Int = 10
    var b: Double = 11.2
    var c: String
    c = "str"
    when(i) {
    1 -> { i = 4}
    else -> {c = i - 10}
    }
    '''
    prog = mel_parser.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
