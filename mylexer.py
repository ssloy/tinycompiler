import io, sys

class Token(object):
    def __init__(self, t, v, l, i):
        self.type, self.value, self.lineno, self.index = t, v, l, i

    def __repr__(self):
        return f'Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno}, index={self.index})'

class State:
    START   = 0
    COMMENT = 1
    STRING  = 2
    WORD    = 3
    NUMBER  = 4

class WendLexer:
    def tokenize(self, text):
        self.lineno, self.idx = 0, 0
        accum = ''
        state = State.START
        while self.idx<len(text):
            sym1 = text[self.idx+0] if self.idx<len(text)-0 else ' '
            sym2 = text[self.idx+1] if self.idx<len(text)-1 else ' '
            print(sym1, sym2)
            match state:
                case State.START:
                    if sym1.isalpha():
                        pass
#                        state = State.WORD
                    elif sym1.isdigit():
                        pass
#                        state = State.NUMBER
                    elif sym1 == '/' and sym2 == '/':
                        state = State.COMMENT
                        print('COMMENT')
                    elif sym1 == '\n':
                        pass
                    elif sym1 == '"':
                        state = State.STRING
                        print('STRING')
                        yield Token('LTEQ', '<=', self.lineno, self.idx)
                    elif sym1 == '=':
                        if sym2 == '=':
                            print('EQ')
                            self.idx += 1
                        else:
                            print('ASSIGN')
                    elif sym1 == '<':
                        if sym2 == '=':
                            print('LTEQ')
                            self.idx += 1
                        else:
                            print('LT')
                    elif sym1 == '>':
                        if sym2 == '=':
                            print('GTEQ')
                            self.idx += 1
                        else:
                            print('GT')
                    elif sym1 == '!':
                        if sym2 == '=':
                            print('NOTEQ')
                            self.idx += 1
                        else:
                            print('NOT')
                    elif sym1 == '&' and sym2 == '&':
                        print('AND')
                        self.idx += 1
                    elif sym1 == '|' and sym2 == '|':
                        print('OR')
                        self.idx += 1
                    elif sym1 == '+':
                        print('PLUS')
                    elif sym1 == '-':
                        print('MINUS')
                    elif sym1 == '/':
                        print('DIVIDE')
                    elif sym1 == '*':
                        print('TIMES')
                    elif sym1 == '%':
                        print('MOD')
                    elif sym1 == '(':
                        print('LPAREN')
                    elif sym1 == ')':
                        print('RPAREN')
                    elif sym1 == '{':
                        print('BEGIN')
                    elif sym1 == '}':
                        print('END')
                    elif sym1 == ';':
                        print('SEMICOLON')
                    elif sym1 == ':':
                        print('COLON')
                    elif sym1 == ',':
                        print('COMMA')
                case State.COMMENT:
                    if sym2 == '\n':
                        state = State.START

                case State.STRING:
                    if sym1 == '"':
                        state = State.START
                case _:
                    print('Error')

            self.idx += 1

#            try:
#                print(text[self.idx])
#                self.idx += 1
#            except self.idxError:
#                return




if len(sys.argv)!=2:
    sys.exit('Usage: compiler.py path/source.wend')
try:
    f = open(sys.argv[1], 'r')
    lexer = WendLexer()
    tokens = WendLexer().tokenize(f.read())
    for t in tokens:
        print('GNA', t)
except Exception as e:
    print(e)

